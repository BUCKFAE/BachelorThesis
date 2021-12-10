import unittest

from src.pokemon.data_handling.util.species_names import convert_species_to_file_name


class TestUtil(unittest.TestCase):

    def test_calculate_damage(self):
        # TODO: Extend the test
        self.assertEqual(convert_species_to_file_name("Mr. Mime"), "mrmime")



if __name__ == "__main__":
    unittest.main()
