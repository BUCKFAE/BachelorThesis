import json
import logging
import signal
import subprocess
import unittest
import os

from poke_env.environment.move import Move

from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator, extract_evs_ivs_from_build, \
    get_total_stat
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.config import GENERATED_DATA_PATH


class TestDamageCalculator(unittest.TestCase):

    def test_calculate_damage(self):
        """Testing the expected damage a Pokémon will deal to another Pokémon"""

        # TODO: Use gerated Pokemon

        # Salamence
        build1 = PokemonBuild("salamence", 76, "MALE", "heavydutyboots", "moxie")
        build1._possible_builds = [(
            {"ability": "moxie",
             "stats": {"hp": 269, "atk": 249, "def": 166, "spa": 211, "spd": 166, "spe": 196},
             "gender": "male", "item": "heavydutyboots", "level": 76,
             "moves": "dragondance|dualwingbeat|earthquake|outrage"}, 1)]

        # Charizard
        build2 = PokemonBuild("charizard", 82, "MALE", "heavydutyboots", "solarpower")
        build2._possible_builds = [(
            {"ability": "solarpower",
             "stats": {"hp": 262, "atk": 185, "def": 175, "spa": 226, "spd": 187, "spe": 211},
             "gender": "male",
             "item": "heavydutyboots",
             "level": 82,
             "moves": "airslash|earthquake|fireblast|roost"}, 1)]


        d = DamageCalculator()

        # Outrage
        outrage_damage = d.calculate_damage(build1, build2, Move("outrage"), None, None, None)
        assert outrage_damage == [141, 142, 144, 145, 147, 148, 151, 153, 154, 156, 157, 159, 160, 162, 163, 166]

        # Earthquake
        outrage_damage = d.calculate_damage(build1, build2, Move("earthquake"), None, None, None)
        assert outrage_damage == [0]

        # Boosted
        boosts_attacker = {"atk": 4, "def": 2, "spa": -1, "spd": 4, "spe": 4}
        boosts_defender = {"atk": -2, "def": 2, "spa": -4, "spd": 2, "spe": -5}
        outrage_damage = d.calculate_damage(build1, build2, Move("outrage"), None, boosts_attacker, boosts_defender)
        assert outrage_damage == [210, 211, 214, 217, 219, 222, 225, 226, 229, 232, 234, 237, 240, 241, 244, 247]


if __name__ == "__main__":
    unittest.main()
