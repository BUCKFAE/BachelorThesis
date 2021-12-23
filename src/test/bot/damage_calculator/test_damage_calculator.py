import json
import logging
import signal
import subprocess
import unittest
import os

from poke_env.environment import status
from poke_env.environment.battle import Battle
from poke_env.environment.move import Move

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator, extract_evs_ivs_from_build, \
    get_total_stat
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.move_result import MoveResult
from src.pokemon.config import GENERATED_DATA_PATH
from src.pokemon.data_handling.util.pokemon_creation import load_build_from_file, build_from_pokemon, pokemon_from_build


class TestDamageCalculator(unittest.TestCase):
    """Testing the Damage Calculator

    - Simple Attacking with no special effects [DONE]
    - Stat boosts (Swords Dance) [DONE]
    - Status changes (BRN)
    - Field effects (Reflect) TODO
    - Dynamax TODO
    - Abilities TODO
        - Levitate
    - Pokemon with different forms TODO
        - Gastrodon
        - Wishiwashi
        - Zygarde
        - Shedinja
    - Changes to the field after the attack TODO
        - Weather
        - Reflect
    """

    def test_damage_calculator_basic(self):
        """Tests a very basic example where Charizard attacks Salamence"""

        build1 = load_build_from_file("charizard")
        build2 = load_build_from_file("salamence")

        damage_calculator = DamageCalculator()

        # Air Slash
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("airslash"))
        assert res1.damage_range == [90, 91, 91, 93, 94, 94, 96, 97, 99, 99, 100, 102, 102, 103, 105, 106]

        # Earthquake
        res2: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("earthquake"))
        assert res2.damage_range == [0]

        # Fire Blast
        res3: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("fireblast"))
        assert res3.damage_range == [65, 66, 66, 67, 68, 69, 69, 70, 71, 72, 72, 73, 74, 75, 75, 77]

        # Focus Blast
        res4: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("focusblast"))
        assert res4.damage_range == [48, 48, 49, 49, 50, 50, 51, 51, 52, 53, 53, 54, 54, 55, 55, 56]

    def test_damage_calculator_stat_boosts(self):
        """Tests attack with stat boosts"""

        build1 = load_build_from_file("charizard")
        build2 = load_build_from_file("garchomp")
        pokemon1 = pokemon_from_build(build1)
        pokemon2 = pokemon_from_build(build2)

        # Increasing stats of charizard
        pokemon1.boosts["atk"] = 1
        pokemon1.boosts["def"] = 2
        pokemon1.boosts["spa"] = 3
        pokemon1.boosts["spd"] = 4
        pokemon1.boosts["spe"] = 5

        # Decreasing stats of garchomp
        pokemon2.boosts["atk"] = - 1
        pokemon2.boosts["def"] = - 2
        pokemon2.boosts["spa"] = - 3
        pokemon2.boosts["spd"] = - 4
        pokemon2.boosts["spe"] = - 5

        damage_calculator = DamageCalculator()

        # Charizard: Air Slash
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("airslash"),
                                                              attacker_pokemon=pokemon1, defender_pokemon=pokemon2)
        assert res1.damage_range == [145, 147, 150, 151, 153, 154, 156, 157, 159, 162, 163, 165, 166, 168, 169, 172]

        # Charizard: Earthquake
        res2: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("earthquake"),
                                                              attacker_pokemon=pokemon1, defender_pokemon=pokemon2)
        assert res2.damage_range == [145, 147, 150, 151, 153, 154, 156, 157, 159, 162, 163, 165, 166, 168, 169, 172]

        # Garchomp: Fire Blast
        res3: MoveResult = damage_calculator.calculate_damage(build2, build1, Move("fireblast"),
                                                              attacker_pokemon=pokemon2, defender_pokemon=pokemon1)
        assert res3.damage_range == [8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10]

        # Garchomp: Outrage
        res4: MoveResult = damage_calculator.calculate_damage(build2, build1, Move("outrage"),
                                                              attacker_pokemon=pokemon2, defender_pokemon=pokemon2)
        assert res4.damage_range == [64, 64, 66, 66, 67, 67, 69, 69, 70, 70, 72, 72, 73, 73, 75, 76]

    def test_damage_calculator_status_effect(self):

        build1 = load_build_from_file("charizard")
        build2 = load_build_from_file("garchomp")
        pokemon1 = pokemon_from_build(build1)
        pokemon2 = pokemon_from_build(build2)

        # Garchomp is burned
        pokemon1.status = status.Status.BRN

        damage_calculator = DamageCalculator()

        # Burned physical attack
        res: MoveResult = damage_calculator.calculate_damage(build2, build1, Move("fireblast"),
                                                             attacker_pokemon=pokemon2, defender_pokemon=pokemon1)
        assert res.damage_range == [62, 63, 64, 65, 65, 66, 67, 68, 68, 69, 70, 71, 71, 72, 73, 74]


if __name__ == "__main__":
    unittest.main()
