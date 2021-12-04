import datetime
import os
import subprocess
import re
import logging

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


    p = subprocess.Popen(["npm", "run", "start"] + [str(i) for i in calculator_args], stdout=subprocess.PIPE)
    out, err = p.communicate()

    out = out.decode("utf-8")
    out = out.split("---START---", maxsplit=1)[1].rsplit("---END---", maxsplit=1)[0]

    print(out)


if __name__ == "__main__":



    build1 = PokemonBuild("Charizard", 90)
    build1.confirmed_moves = ["airslash", "earthquake", "fireblast", "workup"]
    build1.confirmed_item = "Heavy-Duty Boots"
    build1.confirmed_ivs = {"atk": 3, "def": 31, "hp": 20, "spa": 6, "spd": 3, "spe": 7}
    build1.confirmed_evs = {"atk": 54, "def": 87, "hp": 23, "spa": 2, "spd": 252, "spe": 252}


    # TODO: Use other pokemon
    build2 = PokemonBuild("Dragapult", 78)
    build2.confirmed_moves = ["dracometeor", "fireblast", "shadowball", "thunderbolt"]
    build2.confirmed_item = "Choice Specs"
    build2.confirmed_evs = {"atk": 85, "def": 85, "hp": 81, "spa": 85, "spd": 85, "spe": 85}
    build2.confirmed_ivs = {"atk": 31, "def": 31, "hp": 31, "spa": 31, "spd": 31, "spe": 31}

    start = datetime.datetime.now()

    os.chdir("src/pokemon/damage-calculator")

    for _ in range(1):
        calculate_damage(build1, build2, Move("airslash"), None)

    end = datetime.datetime.now()
    print(f"Duration: {(end - start)} ms")
