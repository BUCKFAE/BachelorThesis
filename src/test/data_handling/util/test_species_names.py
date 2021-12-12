import logging
import unittest

from src.pokemon.data_handling.util.species_names import convert_species_name


class TestSpeciesNames(unittest.TestCase):

    def test_convert_species_name(self):
        """Ensuring we correctly handle special species names"""

        # Special characters in names
        self.assertEqual(convert_species_name("Mr. Mime"), "mrmime")

        # TODO: Handling of different Zygarde forms
        self.assertEqual(convert_species_name("Zygarde-10"), "zygarde10")

        # TODO: Wishiwashischool
        # TODO: Aegislashblade
        # TODO: Darmanitanzen

if __name__ == "__main__":
    unittest.main()
