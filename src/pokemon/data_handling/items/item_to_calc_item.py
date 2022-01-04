import re


def item_to_calc_item(item: str) -> str:

    with open(f'src/pokemon/data_handling/items/items.txt') as f:
        all_items = [i.strip() for i in f.readlines()]
        for current_item in all_items:
            if re.sub('[ ]+', '', current_item.lower()) == item:
                return current_item


