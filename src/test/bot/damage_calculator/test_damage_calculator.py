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
from src.pokemon.data_handling.util.pokemon_creation import load_build_from_file


class TestDamageCalculator(unittest.TestCase):

    def test_calculate_damage_basic(self):
        """Testing the expected damage a Pokémon will deal to another Pokémon"""

        # TODO: Use gerated Pokemon
        # TODO: Broken Pokemon
        # Gastrodon

        build1 = load_build_from_file("salamence")
        build2 = load_build_from_file("charizard")

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

    def test_calculate_damage_gastrodon(self):
        """
        Gastrodon exists in two variants in poke-env:
            - gastrodon: west (brown)
            - gastrodoneast: east (green)
        Passing gastrodoneast to the cli tool will break it as the damage calculator uses
            gastrodon for both east and west.
        """

        build1 = load_build_from_file("gastrodon")
        build2 = load_build_from_file("gastrodoneast")

        d = DamageCalculator()

        # West attacking East
        earthquake_damage_1 = d.calculate_damage(build1, build2, Move("earthquake"), None, None, None)
        assert earthquake_damage_1 == [105, 106, 108, 109, 109, 111, 112, 114, 115, 117, 117, 118, 120, 121, 123, 124]

        # East attacking West
        earthquake_damage_2 = d.calculate_damage(build2, build1, Move("earthquake"), None, None, None)
        assert earthquake_damage_2 == [105, 106, 108, 109, 109, 111, 112, 114, 115, 117, 117, 118, 120, 121, 123, 124]

    def test_calculate_damage_zygarde(self):
        """
        Zygarde has three forms
            - Zygarde
            - Zygarde-10%
            - Zygarde-Complete
        """

        build1 = load_build_from_file("zygarde")
        build2 = load_build_from_file("zygarde10")
        build3 = load_build_from_file("zygardecomplete")

        d = DamageCalculator()

        # Zygarde vs Zygarde
        d1 = d.calculate_damage(build1, build1, Move("outrage"), None, None, None)
        assert d1 == [162, 164, 164, 168, 168, 170, 174, 174, 176, 180, 180, 182, 186, 186, 188, 192]

        # Zygarde vs Zygarde10
        d2 = d.calculate_damage(build1, build2, Move("outrage"), None, None, None)
        assert d2 == [204, 206, 210, 212, 216, 216, 218, 222, 224, 228, 228, 230, 234, 236, 240, 242]

        # Zygarde vs ZygardeComplete
        d3 = d.calculate_damage(build1, build3, Move("outrage"), None, None, None)
        assert d3 == [162, 164, 164, 168, 168, 170, 174, 174, 176, 180, 180, 182, 186, 186, 188, 192]

    def test_calculate_damage_wishiwashi(self):
        logging.warning("WISHIWASHI is still brkoken?")


if __name__ == "__main__":
    unittest.main()
