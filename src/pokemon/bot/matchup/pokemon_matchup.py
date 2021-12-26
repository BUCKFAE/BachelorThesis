"""Stores matchup information of two Pokemon"""
from typing import List, Dict

from poke_env.environment.pokemon import Pokemon

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.field.field_state import FieldState
from src.pokemon.bot.matchup.move_result import MoveResult
from src.pokemon.config import MATCHUP_MOVES_DEPTH


class PokemonMatchup:

    def __init__(self,
                 build_p1: PokemonBuild,
                 pokemon_1: Pokemon,
                 build_p2: PokemonBuild,
                 pokemon_2: Pokemon,
                 optimal_moves_p1: List[MoveResult],
                 optimal_moves_p2: List[MoveResult]):
        # Optimal moves for both pokemon
        self._optimal_moves_p1 = optimal_moves_p1
        self._optimal_moves_p2 = optimal_moves_p2
        self.pokemon_1 = pokemon_1
        self.pokemon_2 = pokemon_2

        logger.info(f'Created matchup: {build_p1.species} vs {build_p2.species}')

    def get_optimal_moves_for_species(self, species: str) -> List[MoveResult]:
        """Optimal moves that result in the most amount of damage dealt.
        This includes moves like Swords Dance.
        """
        if self.pokemon_1.species == species:
            return self._optimal_moves_p1
        elif self.pokemon_2.species == species:
            return self._optimal_moves_p2
        else:
            raise ValueError(f'Unknown species in Pokemon matchup!\n'
                             f'Known: {self.pokemon_1.species} and {self.pokemon_2.species}\n'
                             f'Received: {species}')

    def get_expected_damage_after_turns(self, species: str, num_turns: int = MATCHUP_MOVES_DEPTH) -> float:
        """Returns the expected amount of damage received by the specified Pokemon"""
        move_results = self.get_optimal_moves_for_species(species)[:num_turns]
        return sum([m.get_average_damage() for m in move_results]) / len(move_results)

    def get_min_damage_after_turns(self, species: str, num_turns: int) -> int:
        """Returns the minimal amount of damage received by the specified Pokemon"""
        raise NotImplementedError

    def get_max_damage_after_turns(self, species: str, num_turns: int) -> int:
        """Returns the maximal amount of damage received by the specified Pokemon"""
        raise NotImplementedError

    def get_field_after_moves(self, num_turns: int) -> FieldState:
        """Returns the expected field state after num_turns if both Pokemon move optimally"""
        raise NotImplementedError

    def get_stat_changes_after_moves(self, species: str, num_turns: int) -> Dict[int, str]:
        """Returns the stat changes of the given Pokemon after num_turns"""
        raise NotImplementedError

    def is_check(self, species1: str, species2: str) -> bool:
        """Returns True if species1 checks species2, False otherwise"""
        hp_p1 = self.pokemon_1.current_hp
        hp_p2 = self.pokemon_2.current_hp

        # Fraction of hp loss for both pokemon
        damage_taken_p1_frac = self.get_expected_damage_after_turns(species2) / hp_p1
        damage_taken_p2_frac = self.get_expected_damage_after_turns(species1) / hp_p2

        is_check = damage_taken_p1_frac < damage_taken_p2_frac

        # Flipping if names were incorrect order
        if species1 == self.pokemon_2.species:
            is_check = not is_check

        return is_check

    def is_counter(self, species1: str, species2: str) -> bool:
        """Returns True if species1 is a counter to species2"""

        if MATCHUP_MOVES_DEPTH == 1:
            logger.critical(f'isCounter does not work for a depth of 1!')
            return False

        hp_p1 = self.pokemon_1.current_hp
        hp_p2 = self.pokemon_2.current_hp

        # Fraction of hp loss for both pokemon
        damage_taken_p1_frac = self.get_expected_damage_after_turns(species1) / hp_p1
        damage_taken_p2_frac = self.get_expected_damage_after_turns(species2, MATCHUP_MOVES_DEPTH - 1) / hp_p2

        is_counter = damage_taken_p1_frac < damage_taken_p2_frac

        # Flipping if names were incorrect order
        if species1 == self.pokemon_2.species:
            is_counter = not is_counter

        return is_counter


    def is_wall(self, species1: str, species2: str) -> bool:
        """Returns True if species1 can wall against species1"""
        raise NotImplementedError

    def expected_turns_until_faint(self, species: str):
        """Returns the minimum amount of turns the given species will survive this matchup"""
        raise NotImplementedError
