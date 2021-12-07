import datetime
import json
import os
import random
import subprocess
import re
import logging
import time
from typing import Tuple, Dict

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon

from src.pokemon.bot.pokemon_build import PokemonBuild

logging.basicConfig(level=logging.DEBUG)


def get_calc_result(
        p1_species: str,
        p2_species: str,
        move: str
) -> str:
    p = subprocess.Popen("ls", stdout=subprocess.PIPE)
    out, err = p.communicate()


def calculate_damage(attacker: PokemonBuild, defender: PokemonBuild, move: Move, battle: AbstractBattle):
    # TODO: Include battle info
    if battle is None:
        logging.warning("Battle is not specified!")

    logging.debug(f"Calculating damage for {attacker.species} vs {defender.species} (move: {move.id})")

    calculator_args = [
        attacker.species,
        attacker.species,  # TODO: this is the form of the pokemon
        "Male",  # TODO: Gender
        attacker.level,
        attacker.base_stats,
        attacker.confirmed_ivs,
        attacker.confirmed_evs,
        {"atk": -3, "def": 2, "spa": 2, "spd": 0, "spe": 0},  # TODO: Boosts, will later be always zero
        "Hardy",  # All Pokémon have neutral nature
        "Blaze",  # TODO: Ability
        attacker.confirmed_item,
        "",  # No status
        262,  # TODO: HP
        False,  # Not Dynamaxed
        defender.species,
        defender.species,  # TODO: this is the form of the pokemon
        "Male",  # TODO: Gender
        defender.level,
        defender.base_stats,
        defender.confirmed_ivs,
        defender.confirmed_evs,
        {"atk": -3, "def": 2, "spa": 2, "spd": 0, "spe": 0},  # TODO: Boosts, will later be always zero
        "Hardy",  # All Pokémon have neutral nature
        "Clear Body",  # TODO: Ability
        defender.confirmed_item,
        "",  # No status
        265,  # TODO: HP
        False,  # Not Dynamaxed
        move.id
    ]

    p = subprocess.Popen(["npm run start"],
                         stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    time.sleep(5)

    for request_count in [1, 2, 3, 4, 5, 7, 10, 20, 50, 100, 500, 1000, 5000, 10_000, 25_000, 50_000]:

        start = datetime.datetime.now()

        for _ in range(request_count):

            # Modifying calc input
            calculator_args[2] = random.choice(["Male", "Female"])  # Gender
            calculator_args[3] = random.randint(5, 90)  # Level
            calculator_args[12] = random.randint(20, 200)  # HP
            calculator_args[16] = random.choice(["Male", "Female"])  # Gender
            calculator_args[17] = random.randint(5, 90)  # Level
            calculator_args[26] = random.randint(20, 200)  # HP

            calc_input = (";;".join([str(i) for i in calculator_args]) + "\n").encode()

            p.stdin.write(calc_input)
            p.stdin.flush()

            output = []
            while True:
                res = p.stdout.readline().decode().strip()
                if res == "DONE!":
                    break

                output.append(res)

        end = datetime.datetime.now()
        print(f"Requests: {request_count:05d}: {(end - start)} ms")

    p.kill()

    # print("Output:\n\t{}".format("\n\t".join(output)))

    # out = out.decode("utf-8")
    # out = out.split("---START---", maxsplit=1)[1].rsplit("---END---", maxsplit=1)[0]

    # print(out)


def extract_evs_ivs_from_build(pokemon: PokemonBuild) -> Tuple[Dict[str, int], Dict[str, int]]:
    assumed_ivs = {"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31}
    assumed_evs = {"hp": 85, "atk": 85, "def": 85, "spa": 85, "spd": 85, "spe": 85}

    # On some Pokémon these stats occur along a 31 iv stat
    possible_evs = [0, 48, 80, 84]

    # Getting assumed ivs and evs
    for key, value in pokemon.confirmed_stats.items():

        # If the stat is not (31 / 85) it's (0, 0)
        if _get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key) \
                != pokemon.confirmed_stats[key]:
            assumed_ivs[key] = 0
            assumed_evs[key] = 0

            # Nether (31 / 85) nor (0 / 0)
            if _get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key) \
                    != pokemon.confirmed_stats[key]:

                for possible_ev in possible_evs:
                    assumed_ivs[key] = 31
                    assumed_evs[key] = possible_ev

                    res = _get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key)
                    if res == pokemon.confirmed_stats[key]:
                        print(f"Found")
                        break

            estimate = _get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key)

            if estimate != pokemon.confirmed_stats[key]:
                raise ValueError(f"Stat \"{key}\" was not matching for \"{pokemon.species}\""
                      f"\n\texpected: {pokemon.confirmed_stats[key]} actual: {estimate} ")

    return assumed_evs, assumed_ivs


def _get_evs(base: Dict[str, int], stats: Dict[str, int], ivs: Dict[str, int], level: int, stat: str) -> int:
    temp1 = int(((stats[stat] - 5) * 100) / (level)) - (2 * base[stat])
    return int(temp1 - (ivs[stat] / 4))


def _get_ivs(base: Dict[str, int], stats: Dict[str, int], evs: Dict[str, int], level: int, stat: str) -> int:
    temp1 = int(((stats[stat] - 5) * 100) / (level)) - (2 * base[stat])
    return (temp1 - evs[stat]) * 4


def _get_total_stat(base: Dict[str, int], evs: Dict[str, int], ivs: Dict[str, int], level: int, stat: str) -> int:
    # Different formula for HP stat
    if stat == "hp":
        temp1 = (2 * base[stat] + ivs[stat] + int(evs[stat] / 4)) * level
        return int(temp1 / 100) + level + 10

    temp1 = (2 * base[stat] + ivs[stat] + int(evs[stat] / 4)) * level
    return int(temp1 / 100) + 5


def validate_all_build_stats():
    print("Validating all builds")

    for path, _, files in os.walk("src/pokemon/replays/data/generated"):
        for name in files:
            assert name.endswith(".txt")

            species = name.removesuffix(".txt")

            print(f"Pokemon: {species}")

            with open(os.path.join(path, species) + ".txt") as replay_file:

                # Base stats are always the same regardless of level

                for build_string in [b.strip() for b in replay_file.readlines() if b.strip()]:
                    print(f"{build_string}")
                    build = json.loads(build_string.split(" - ")[1])

                    pokemon_build = PokemonBuild(species, build["level"])
                    pokemon_build.confirmed_stats = build["stats"]

                    evs, ivs = extract_evs_ivs_from_build(pokemon_build)
                    for stat in build["stats"]:
                        calculated_stat = _get_total_stat(pokemon_build.base_stats, evs, ivs, build["level"], stat)
                        assert calculated_stat == build["stats"][stat]


if __name__ == "__main__":
    build1 = PokemonBuild("Charizard", 82)
    build1.confirmed_moves = ["airslash", "earthquake", "fireblast", "workup"]
    build1.confirmed_item = "Heavy-Duty Boots"
    build1.confirmed_stats = {"atk": 185, "def": 175, "spa": 226, "spd": 187, "spe": 211}

    # ev, iv = _stats_to_input(build1)
    # print(f"{ev=}\n{iv=}")

    validate_all_build_stats()

    # calculate_damage(build1, build2, Move("airslash"), None)
