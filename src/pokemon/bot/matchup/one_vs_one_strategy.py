from typing import List, Optional

from src.pokemon import logger
from src.pokemon.bot.matchup.move_result import MoveResult


class OneVsOneStrategy:
    """Stores how to play with the current Pokemon against the enemy Pokemon"""

    def __init__(self,
                 own_species: str,
                 enemy_species: str,
                 moves_to_perform: List[MoveResult]):
        self.own_species = own_species
        self.enemy_species = enemy_species
        self.moves_to_perform = moves_to_perform
        self.current_move_id = 0

        logger.info(f'Created a new Strategy for {self.own_species} vs {self.enemy_species}:\n'
                    f'\t{self.moves_to_perform}')

    def get_next_move(self) -> MoveResult:

        assert len(self.moves_to_perform) > self.current_move_id

        next_move = self.moves_to_perform[self.current_move_id]
        self.current_move_id += 1
        return next_move

    def needs_update(self, species_p1: str, species_p2: str, own_possible_moves: List[str]) -> bool:
        return not(species_p1 == self.own_species and \
            species_p2 == self.enemy_species and \
            len(self.moves_to_perform) > self.current_move_id and \
            all([m.move in [a for a in own_possible_moves] for m in self.moves_to_perform]))
