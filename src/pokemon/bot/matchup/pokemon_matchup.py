"""Stores matchup information of two Pokemon"""
from poke_env.environment.pokemon import Pokemon

from src.pokemon import logger
from typing import List, Dict

from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.field.field_state import FieldState


class PokemonMatchup:

    def __init__(self,
                 build_p1: PokemonBuild,
                 pokemon_1: Pokemon,
                 build_p2: PokemonBuild,
                 pokemon_2: Pokemon):

        # Optimal moves for both pokemon
        self._optimal_moves_p1 = None
        self._optimal_moves_p2 = None
        self.pokemon_1 = pokemon_1
        self.pokemon_2 = pokemon_2

        logger.info(f'Created matchup: {build_p1.species} vs {build_p2.species}')

    def get_optimal_moves_(self, species: str) -> List[str]:
        """Optimal moves that result in the most amount of damage dealt.
        This includes moves like Swords Dance.
        """
        raise NotImplementedError

    def get_expected_damage_after_moves(self, species: str, num_turns: int) -> float:
        """Returns the expected amount of damage received by the specified Pokemon"""
        raise NotImplementedError

    def get_min_damage_after_moves(self, species: str, num_turns: int) -> int:
        """Returns the minimal amount of damage received by the specified Pokemon"""
        raise NotImplementedError

    def get_max_damage_after_moves(self, species: str, num_turns: int) -> int:
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
        raise NotImplementedError

    def is_counter(self, species1: str, species2: str) -> bool:
        """Returns True if species1 is a counter to species2"""
        raise NotImplementedError

    def is_wall(self, species1: str, species2: str) -> bool:
        """Returns True if species1 can wall against species1"""
        raise NotImplementedError

    def expected_turns_until_faint(self, species: str):
        """Returns the minimum amount of turns the given species will survive this matchup"""
        raise NotImplementedError
