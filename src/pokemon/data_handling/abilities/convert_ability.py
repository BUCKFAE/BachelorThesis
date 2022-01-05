import re

from singleton_decorator import singleton


@singleton
class AbilityTranslator:
    ability_table = {}

    def __init__(self):
        if not self.ability_table:
            with open(f'src/pokemon/data_handling/abilities/ability_list.txt') as f:
                all_abilities = [a.strip() for a in f.readlines()]
                for current_ability in all_abilities:
                    self.ability_table[re.sub("[0-9- ]+", "", current_ability).lower()] = current_ability


    def ability_to_calc_ability(self, ability: str) -> str:
        return self.ability_table[ability]