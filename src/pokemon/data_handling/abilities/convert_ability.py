import re


def get_calculator_ability(ability: str) -> str:
    """Convert ability from poke-env format to damage calculator format"""
    with open(f'src/pokemon/data_handling/abilities/ability_list.txt') as f:
        all_abilities = [a.strip() for a in f.readlines()]
        for current_ability in all_abilities:
            if re.sub("[0-9 ]+", "", current_ability).lower() == ability:
                return current_ability
