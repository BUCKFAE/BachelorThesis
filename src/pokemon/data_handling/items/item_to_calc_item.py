import re

from singleton_decorator import singleton


@singleton
class ItemTranslator:
    item_table = {}

    def __init__(self):
        if not self.item_table:
            with open(f'src/pokemon/data_handling/items/items.txt') as f:
                all_items = [i.strip() for i in f.readlines()]
                for current_item in all_items:
                    self.item_table[re.sub('[ -]+', '', current_item.lower())] = current_item

    def item_to_calc_item(self, item: str) -> str:

        if item is None or item == 'None':
            return ''

        return self.item_table[item]
