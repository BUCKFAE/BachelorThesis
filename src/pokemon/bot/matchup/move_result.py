"""Contains all information about a move in a battle"""

from typing import List

from src.pokemon import logger


class MoveResult:

    def __init__(self,
                 species_p1: str,
                 species_p2: str,
                 move: str,
                 damage_range: List[str],
                 new_field_state: ):

        logger.info(f'MoveResult: {species_p1} vs {species_p2}: {move}')
