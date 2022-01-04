import unittest

from src.pokemon.data_handling.items.item_to_calc_item import ItemTranslator


class TestItemTranslator(unittest.TestCase):

    def test_item_translator(self):

        t = ItemTranslator()

        assert t.item_to_calc_item('heavydutyboots') == 'Heavy-Duty Boots'

        t2 = ItemTranslator()
        assert t2.item_to_calc_item('lifeorb') == 'Life Orb'

if __name__ == "__main__":
    unittest.main()