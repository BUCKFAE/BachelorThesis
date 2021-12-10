import datetime
import json
import os
import random
import re
import subprocess
import logging
import atexit
import time
from typing import Tuple, Dict

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move

from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.config import NODE_LIB_PATH

logging.basicConfig(level=logging.WARNING)


class DamageCalculator:

    def __init__(self):
        self.cli_tool = subprocess.Popen(["npm run start"],
                                         cwd=NODE_LIB_PATH,
                                         stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        atexit.register(self.cli_tool.kill)

    def calculate_damage(
            self,
            attacker: PokemonBuild,
            defender: PokemonBuild,
            move: Move,
            battle: AbstractBattle,
            boosts_attacker=None,
            boosts_defender=None
    ):
        # TODO: Status
        # TODO: Field
        # TODO: Dynamax

        if boosts_attacker is None:
            boosts_attacker = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "hp": 0}

        if boosts_defender is None:
            boosts_defender = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "hp": 0}
        if battle is None:
            logging.info("Battle is not specified!")

        logging.debug(f"Calculating damage for {attacker.species} vs {defender.species} (move: {move.id})")

        attacker_evs, attacker_ivs = extract_evs_ivs_from_build(attacker)
        defender_evs, defender_ivs = extract_evs_ivs_from_build(defender)

        calculator_args = [
            attacker.species,
            attacker.species,  # TODO: this is the form of the pokemon
            "M" if attacker.gender == "male" else ("F" if attacker.gender == "female" else "N"),
            attacker.level,
            attacker.base_stats,
            attacker_ivs,
            attacker_evs,
            boosts_attacker,
            "Hardy",  # All Pokémon have neutral nature
            attacker.get_most_likely_ability(),
            attacker.get_most_likely_item(),
            "",  # No status
            attacker.get_most_likely_stats()["hp"],
            False,  # Not Dynamaxed
            defender.species,
            defender.species,  # TODO: this is the form of the pokemon
            "M" if defender.gender == "Male" else ("F" if defender.gender == "Female" else "N"),
            defender.level,
            defender.base_stats,
            defender_ivs,
            defender_evs,
            boosts_defender,
            "Hardy",  # All Pokémon have neutral nature
            defender.get_most_likely_ability(),
            defender.get_most_likely_item(),
            "",  # No status
            defender.get_most_likely_stats()["hp"],
            False,  # Not Dynamaxed
            move.id
        ]

        # TODO: THIS LEAKS MEMORY!!!!

        calc_input = (";;".join([str(i) for i in calculator_args]) + "\n").encode()

        self.cli_tool.stdin.write(calc_input)
        self.cli_tool.stdin.flush()

        output = []
        while True:
            res = self.cli_tool.stdout.readline().decode().strip()
            if res == "DONE!":
                break
            output.append(res)

        # Getting the damage ranges
        res = [e for e in output if re.match("damage: [0-9]+,", e)]
        if res:
            res = res[0]
        else:
            start_index = output.index("damage: [")
            end_index = output[start_index:].index("],")
            res = "".join(output[start_index:start_index + end_index])
        ranges_text = re.sub("[^0-9,]", "", res)
        ranges = [int(i) for i in ranges_text.split(",") if i]

        return ranges


def extract_evs_ivs_from_build(pokemon: PokemonBuild) -> Tuple[Dict[str, int], Dict[str, int]]:
    assumed_ivs = {"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31}
    assumed_evs = {"hp": 85, "atk": 85, "def": 85, "spa": 85, "spd": 85, "spe": 85}

    # On some Pokémon these stats occur along a 31 iv stat
    possible_evs = [0, 48, 80, 84]

    # Getting assumed ivs and evs
    for key, value in pokemon.get_most_likely_stats().items():

        # If the stat is not (31 / 85) it's (0, 0)
        if get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key) \
                != pokemon.get_most_likely_stats()[key]:
            assumed_ivs[key] = 0
            assumed_evs[key] = 0

            # Nether (31 / 85) nor (0 / 0)
            if get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key) \
                    != pokemon.get_most_likely_stats()[key]:

                for possible_ev in possible_evs:
                    assumed_ivs[key] = 31
                    assumed_evs[key] = possible_ev

                    res = get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key)
                    if res == pokemon.get_most_likely_stats()[key]:
                        break

            estimate = get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key)

            if estimate != pokemon.get_most_likely_stats()[key]:
                raise ValueError(f"Stat \"{key}\" was not matching for \"{pokemon.species}\""
                                 f"\n\texpected: {pokemon.get_most_likely_stats()[key]} actual: {estimate} ")

    return assumed_evs, assumed_ivs


def _get_evs(base: Dict[str, int], stats: Dict[str, int], ivs: Dict[str, int], level: int, stat: str) -> int:
    temp1 = int(((stats[stat] - 5) * 100) / (level)) - (2 * base[stat])
    return int(temp1 - (ivs[stat] / 4))


def _get_ivs(base: Dict[str, int], stats: Dict[str, int], evs: Dict[str, int], level: int, stat: str) -> int:
    temp1 = int(((stats[stat] - 5) * 100) / (level)) - (2 * base[stat])
    return (temp1 - evs[stat]) * 4


def get_total_stat(base: Dict[str, int], evs: Dict[str, int], ivs: Dict[str, int], level: int, stat: str) -> int:
    # Different formula for HP stat
    if stat == "hp":
        temp1 = (2 * base[stat] + ivs[stat] + int(evs[stat] / 4)) * level
        return int(temp1 / 100) + level + 10

    temp1 = (2 * base[stat] + ivs[stat] + int(evs[stat] / 4)) * level
    return int(temp1 / 100) + 5
