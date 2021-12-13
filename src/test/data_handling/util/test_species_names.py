import logging
import unittest

from src.pokemon.data_handling.util.species_names import convert_species_name


class TestSpeciesNames(unittest.TestCase):

    def test_convert_species_name(self):
        assert convert_species_name("p2: Dracovish") == "dracovish"
        assert convert_species_name("Dracovish") == "dracovish"


if __name__ == "__main__":
    unittest.main()
