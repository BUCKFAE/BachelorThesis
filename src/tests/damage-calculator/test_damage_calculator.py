import unittest
from src import pokemon
from pokemon import damage_calculator
from pokemon.damage_calculator.damage_calculator import calculate_damage, validate_all_build_stats
from src.pokemon.bot.pokemon_build import PokemonBuild

class TestDamageCalculator(unittest.TestCase):

    def test_calculate_damage(self):

        build1 = PokemonBuild("Charizard", 82, "Male")
        build1.confirmed_moves = ["airslash", "earthquake", "fireblast", "workup"]
        build1.confirmed_item = "Heavy-Duty Boots"
        build1.confirmed_stats = {"atk": 185, "def": 175, "spa": 226, "spd": 187, "spe": 211}
        calculate_damage(None, None, None, None, None, None)

    def test_validate_builds(self):
        """Ensures that we can get extract the evs and ivs of every known pokemon"""
        print("Hello")
        validate_all_build_stats()

if __name__ == "__main__":
    unittest.main()