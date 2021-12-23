import datetime
import json
import os
import random
import re
import subprocess
import atexit
import time
from typing import Tuple, Dict, Optional, List

from poke_env.environment.pokemon import Pokemon
from singleton_decorator import singleton
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.field.field_state import FieldState
from src.pokemon.bot.matchup.move_result import MoveResult
from src.pokemon.config import NODE_DAMAGE_CALCULATOR_PATH


@singleton
class DamageCalculator:
    _cli_tool = None

    def __init__(self):
        if self._cli_tool is None:
            self._cli_tool = subprocess.Popen(["npm run start"],
                                              cwd=NODE_DAMAGE_CALCULATOR_PATH,
                                              stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    def calculate_damage(
            self,
            attacker_build: PokemonBuild,
            defender_build: PokemonBuild,
            move: Move,
            attacker_pokemon: Optional[Pokemon] = None,
            defender_pokemon: Optional[Pokemon] = None,
            field: Optional[FieldState] = None) -> MoveResult:
        # TODO: This has to include current states of the Pokemon

        if boosts_attacker is None:
            boosts_attacker = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "hp": 0}

        if boosts_defender is None:
            boosts_defender = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "hp": 0}
        if battle is None:
            logger.info("Battle is not specified!")

        logger.debug(f"Calculating damage for {attacker.species} vs {defender.species} (move: {move.id})")

        attacker_evs, attacker_ivs = extract_evs_ivs_from_build(attacker)
        defender_evs, defender_ivs = extract_evs_ivs_from_build(defender)

        # TypeScript expects double instead of single quotes
        attacker_evs = re.sub("\'", "\"", str(attacker_evs))
        attacker_ivs = re.sub("\'", "\"", str(attacker_ivs))
        defender_evs = re.sub("\'", "\"", str(defender_evs))
        defender_ivs = re.sub("\'", "\"", str(defender_ivs))

        boosts_attacker = re.sub("\'", "\"", str(boosts_attacker))
        boosts_defender = re.sub("\'", "\"", str(boosts_defender))

        attacker_item = attacker.get_most_likely_item()
        defender_item = defender.get_most_likely_item()

        # TODO: Include current state of both Pokemon (like BRN, lost HP)
        calculator_args = [
            attacker.species,
            attacker.species,  # TODO: this is the form of the pokemon
            "M" if attacker.gender == "male" else ("F" if attacker.gender == "female" else "N"),
            attacker.level,
            re.sub("\"", "\'", str(attacker.base_stats)),
            attacker_ivs,
            attacker_evs,
            re.sub("\'", "\"", str(boosts_attacker)),
            "Hardy",  # All Pokémon have neutral nature
            attacker.get_most_likely_ability(),
            attacker_item if attacker_item != 'broken_item' else '',
            "",  # No status
            attacker.get_most_likely_stats()["hp"],
            False,  # Not Dynamaxed
            defender.species,
            defender.species,  # TODO: this is the form of the pokemon
            "M" if defender.gender == "Male" else ("F" if defender.gender == "Female" else "N"),
            defender.level,
            re.sub("\"", "\'", str(defender.base_stats)),
            defender_ivs,
            defender_evs,
            re.sub("\'", "\"", str(boosts_defender)),
            "Hardy",  # All Pokémon have neutral nature
            defender.get_most_likely_ability(),
            defender_item if defender_item != 'broken_item' else '',
            "",  # No status
            defender.get_most_likely_stats()["hp"],
            False,  # Not Dynamaxed
            move.id
        ]

        # TODO: Fix Aegislash
        if "aegislash" == attacker.species:
            calculator_args[0] = 'aegislashblade'
        if "aegislash" == defender.species:
            calculator_args[14] = 'aegislashblade'

        # Fixing Gastrodon
        # Poke-Env uses 'gastrodon' and 'gastrodoneast' for both variants
        # The damage-calculator uses 'gastrodon' for both variants
        if attacker.species == 'gastrodoneast':
            calculator_args[0] = 'gastrodon'
        if defender.species == 'gastrodoneast':
            calculator_args[14] = 'gastrodon'

        # There are multiple pikachu species, they all have the same base stats and are handled
        # identically by the damage calculator
        if "pikachu" in attacker.species:
            calculator_args[0] = "pikachu"
        if "pikachu" in defender.species:
            calculator_args[14] = "pikachu"

        calculator_args[0] = calculator_args[0].capitalize()
        calculator_args[14] = calculator_args[14].capitalize()

        calc_input = (";;".join([str(i) for i in calculator_args]) + "\n").encode()

        self._cli_tool.stdin.write(calc_input)
        self._cli_tool.stdin.flush()

        # Getting output
        output = []
        while True:
            res = self._cli_tool.stdout.readline().decode().strip()
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

        # TODO: Create moveResult based on calc result
        return MoveResult(None, None, None, None, None)

    def get_optimal_moves(
            self,
            attacker_build: PokemonBuild,
            attacker_pokemon: Optional[Pokemon],
            defender_build: PokemonBuild,
            defender_pokemon: Optional[Pokemon],
            battle: AbstractBattle) -> List[MoveResult]:
        # TODO: Account for disabled moves!!

        best_move = (None, -1)

        logger.info(f"Most likely moves for: {attacker.species}\n\t{attacker.get_most_likely_moves()}")

        for move in attacker.get_most_likely_moves():

            if not move.strip():
                logger.warning('The pokemon has no moves left, using struggle!')
                move = 'struggle'

            # TODO: Use expected damage instead (misses)
            damage_range = self.calculate_damage(
                attacker,
                defender,
                Move(move),
                battle,
                None,
                None
            )
            expected_damage = sum(damage_range) / len(damage_range)
            if expected_damage >= best_move[1]:
                best_move = (move, expected_damage)

        assert best_move[0] is not None
        assert best_move[1] >= 0

        raise NotImplementedError('This has to return MoveResults')


def extract_evs_ivs_from_build(pokemon: PokemonBuild) -> Tuple[Dict[str, int], Dict[str, int]]:
    assumed_ivs = {"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31}
    assumed_evs = {"hp": 85, "atk": 85, "def": 85, "spa": 85, "spd": 85, "spe": 85}

    # On some Pokémon these stats occur along a 31 iv stat
    possible_evs = [0, 48, 76, 80, 84]

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

                # Handling wishiwashi
                if pokemon.species == "wishiwashi":
                    p = Pokemon(species="wishiwashischool")
                    if pokemon.base_stats != p.base_stats:
                        pokemon.base_stats = p.base_stats
                        return extract_evs_ivs_from_build(pokemon)

                ValueError(f"Stat \"{key}\" was not matching for \"{pokemon.species}\""
                           f"\n\texpected: {pokemon.get_most_likely_stats()[key]} actual: {estimate} ")

    return assumed_evs, assumed_ivs


def _get_evs(base: Dict[str, int], stats: Dict[str, int], ivs: Dict[str, int], level: int, stat: str) -> int:
    temp1 = int(((stats[stat] - 5) * 100) / level) - (2 * base[stat])
    return int(temp1 - (ivs[stat] / 4))


def _get_ivs(base: Dict[str, int], stats: Dict[str, int], evs: Dict[str, int], level: int, stat: str) -> int:
    temp1 = int(((stats[stat] - 5) * 100) / level) - (2 * base[stat])
    return (temp1 - evs[stat]) * 4


def get_total_stat(base: Dict[str, int], evs: Dict[str, int], ivs: Dict[str, int], level: int, stat: str) -> int:
    # Different formula for HP stat
    if stat == "hp":

        # Shedinja
        if base["hp"] == 1:
            return 1

        temp1 = (2 * base[stat] + ivs[stat] + int(evs[stat] / 4)) * level
        return int(temp1 / 100) + level + 10

    temp1 = (2 * base[stat] + ivs[stat] + int(evs[stat] / 4)) * level
    return int(temp1 / 100) + 5
