"""Contains all information about a move in a battle"""

from typing import List

from poke_env.environment import status

from src.pokemon import logger
from src.pokemon.bot.matchup.field.field_state import FieldState


class MoveResult:
    def __init__(self,
                 species_p1: str,
                 species_p2: str,
                 move: str,
                 damage_taken_defender: List[int],
                 new_field_state: FieldState,
                 damage_taken_attacker: float = None,
                 damage_healed_attacker: int = None,
                 damage_healed_defender: int = None,
                 new_status_attacker: status.Status = None,
                 new_status_defender: status.Status = None):
        """
        Stores the result of a move in a battle

        :param species_p1: The species of the first Pokemon
        :param species_p2: The species of the second Pokemon
        :param move: The move used
        :param damage_taken_defender: Amount of damage dealt to the defending Pokemon
        :param new_field_state: Field state after the attack
        :param damage_taken_attacker: Recoil damage taken by the attacker
        :param damage_healed_attacker: HP healed by the attacker
        :param damage_healed_defender: HP healed by the defender.
        """

        self.species_p1 = species_p1
        self.species_p2 = species_p2
        self.move = move
        self.damage_taken_defender = damage_taken_defender
        self.damage_taken_attacker = damage_taken_attacker
        self.damage_healed_attacker = damage_healed_attacker
        self.damage_healed_defender = damage_healed_defender
        self.new_status_attacker = new_status_attacker
        self.new_status_defender = new_status_defender
        self.new_field_state = new_field_state

        logger.info(f'MoveResult: {species_p1} vs {species_p2}: {move}')

    def get_min_damage(self) -> int:
        """The smallest possible amount of damage that the move deals to the Pokemon of player 2"""
        return min(self.damage_taken_defender)

    def get_max_damage(self) -> int:
        """The biggest possible amount of damage that the move deals to the Pokemon of player 2"""
        return max(self.damage_taken_defender)

    def get_average_damage(self) -> float:
        """The expected amount of damage that the move deals to the Pokemon of player 2"""
        assert len(self.damage_taken_defender) > 0
        return sum(self.damage_taken_defender) / len(self.damage_taken_defender)
