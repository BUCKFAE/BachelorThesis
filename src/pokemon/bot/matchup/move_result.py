"""Contains all information about a move in a battle"""

from typing import List

from src.pokemon import logger
from src.pokemon.bot.matchup.field.field_state import FieldState


class MoveResult:

    def __init__(self,
                 species_p1: str,
                 species_p2: str,
                 move: str,
                 damage_range: List[int],
                 new_field_state: FieldState):

        self.species_p1 = species_p1
        self.species_p2 = species_p2
        self.move = move
        self.damage_range = damage_range
        self.new_field_state = new_field_state

        logger.info(f'MoveResult: {species_p1} vs {species_p2}: {move}')

    def get_min_damage(self) -> int:
        """The smallest possible amount of damage that the move deals to the Pokemon of player 2"""
        return min(self.damage_range)

    def get_max_damage(self) -> int:
        """The biggest possible amount of damage that the move deals to the Pokemon of player 2"""
        return max(self.damage_range)

    def get_average_damage(self) -> float:
        """The expected amount of damage that the move deals to the Pokemon of player 2"""
        assert len(self.damage_range) > 0
        return sum(self.damage_range) / len(self.damage_range)
