"""Stores matchup information of two Pokemon"""
from math import ceil, floor
from typing import List, Dict, Optional

from poke_env.environment.pokemon import Pokemon

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.field.field_state import FieldState
from src.pokemon.bot.matchup.move_result import MoveResult


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
        self._build_p1 = build_p1
        self._build_p2 = build_p2
        self.pokemon_1 = pokemon_1
        self.pokemon_2 = pokemon_2

        self.len_moves = len(self.get_optimal_moves_for_species(self.pokemon_1.species))

        ## logger.info(f'Created matchup: {build_p1.species} vs {build_p2.species}')

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

    def get_expected_damage_after_turns(self, species: str, num_turns: Optional[int] = None) -> float:
        """Returns the expected amount of damage received by the specified Pokemon
        This uses the expected optimal moves. This means that if a Pokemon is expected to use SwordsDance in
        his first turn, this Method returns an expected damage taken of 0 for the enemy Pokemon.
        This method also accepts zero or a negative amount of num_turns as parameter and will always return zero
        if num_turns is smaller than one. This is done to make MinMax a bit easier as we can then treat the case
        that two pokemon can kill each other in the first turn equal to the case that the two pokemon can kill
        each other in the same turn.
        If num_turns is bigger than the amount of moves collected, we add the average damage.
        """

        if num_turns is None:
            num_turns = self.len_moves

        # Returning zero to make MinMax a bit easier
        if num_turns < 1:
            return 0

        move_results = self.get_optimal_moves_for_species(self.get_opponent(species))

        # Sum of precalculated moves
        if num_turns <= self.len_moves:
            return sum([round(m.get_average_damage()) for m in move_results][:num_turns])

        # Not enough moves precalculated, adding expected damage
        return sum([round(m.get_average_damage()) for m in move_results]) \
            + self.get_average_damage_per_turn(species) * (num_turns - self.len_moves)

    def get_average_damage_per_turn(self, species: str) -> float:
        return round(self.get_expected_damage_after_turns(species) / self.len_moves)

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
        pokemon_1 = self._get_pokemon_from_species(species1)
        pokemon_2 = self._get_pokemon_from_species(species2)

        hp_p1 = round(pokemon_1.current_hp_fraction * self._build_p1.get_most_likely_stats()["hp"])
        hp_p2 = round(pokemon_2.current_hp_fraction * self._build_p2.get_most_likely_stats()["hp"])

        faint_p1 = self.expected_turns_until_faint(species1, hp_p1)
        faint_p2 = self.expected_turns_until_faint(species2, hp_p2)

        if faint_p1 == faint_p2:
            return self._build_p1.get_most_likely_stats()["spe"] > self._build_p2.get_most_likely_stats()["spe"]

        return faint_p1 > faint_p2

    def is_counter(self, species1: str, species2: str) -> bool:
        """Returns True if species1 counters species2, False otherwise"""
        pokemon_1 = self._get_pokemon_from_species(species1)
        pokemon_2 = self._get_pokemon_from_species(species2)

        hp_p1 = round(pokemon_1.current_hp_fraction * self._build_p1.get_most_likely_stats()["hp"])
        hp_p2 = round(pokemon_2.current_hp_fraction * self._build_p2.get_most_likely_stats()["hp"])

        faint_p1 = self.expected_turns_until_faint(species1, hp_p1) - 1
        faint_p2 = self.expected_turns_until_faint(species2, hp_p2)

        if faint_p1 == faint_p2:
            return self._build_p1.get_most_likely_stats()["spe"] > self._build_p2.get_most_likely_stats()["spe"]

        return faint_p1 > faint_p2


    def _get_pokemon_from_species(self, species: str) -> Pokemon:
        """Returns the Pokemon with the name of this species"""
        if self.pokemon_1.species == species:
            return self.pokemon_1
        elif self.pokemon_2.species == species:
            return self.pokemon_2

        raise ValueError(f'The Pokemon {species} does not exist in the given matchup!\n' +
                         f'Known Pokemon: {self.pokemon_1.species} - {self.pokemon_2.species}')

    def is_wall(self, species1: str, species2: str) -> bool:
        """Returns True if species1 can wall against species1
        TODO: Implement this
        """
        return False
        # raise NotImplementedError

    def expected_turns_until_faint(self, species: str, current_hp: Optional[int] = None):
        """Returns the minimum amount of turns the given species will survive this matchup"""
        # TODO: Use this method for isCheck and isCounter instead
        hp = self._get_pokemon_from_species(species).current_hp if current_hp is None else current_hp
        # logger.info(f'{species} HP: {hp}')
        dmg_taken = self.get_average_damage_per_turn(species)
        # logger.info(f'{species} damage taken: {dmg_taken}')
        return ceil(hp / dmg_taken) if dmg_taken > 0 else 50

    def is_battle_between(self, species1: str, species2: str) -> bool:
        """Checks if this matchup is played between the given two pokemon"""
        if species1 == self.pokemon_1.species and species2 == self.pokemon_2.species:
            return True

        if species2 == self.pokemon_2.species and species1 == self.pokemon_1.species:
            raise ValueError(f'Species one and two are swapped in the matchup!\n'
                             f'Always pass in the own species first!')

        return False

    def get_opponent(self, species: str) -> str:
        if species == self.pokemon_1.species:
            return self.pokemon_2.species
        return self.pokemon_1.species
