import unittest
from typing import List

from src.pokemon import logger
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.test.bot.matchup.matchup_creator import MatchupCreator


class TestPokemonMatchup(unittest.TestCase):

    def test_get_expected_damage_after_turns(self):
        matchup_creator = MatchupCreator(team_length=3, moves_depth=4)
        matchups = matchup_creator.get_test_matchups()

        m1: PokemonMatchup = matchups[0]
        logger.info(f'Charizard vs Roserade:\n'
                    f'\tCharizard: {m1.get_optimal_moves_for_species(m1.pokemon_1.species)}\n'
                    f'\tRoserade: {m1.get_optimal_moves_for_species(m1.pokemon_2.species)}')

        # Damage Charizard takes after n turns
        assert m1.get_expected_damage_after_turns('charizard', 1) == 121
        assert m1.get_expected_damage_after_turns('charizard', 2) == 242
        assert m1.get_expected_damage_after_turns('charizard', 3) == 363
        assert m1.get_expected_damage_after_turns('charizard', 10) == 1210

        # Damage Roserade takes after n turns
        assert m1.get_expected_damage_after_turns('roserade', 1) == 212
        assert m1.get_expected_damage_after_turns('roserade', 2) == 424
        assert m1.get_expected_damage_after_turns('roserade', 3) == 636
        assert m1.get_expected_damage_after_turns('roserade', 10) == 2120

        m2: PokemonMatchup = [m for m in matchups if m.is_battle_between('latios', 'absol')][0]
        logger.info(f'Latios vs Absol\n'
                    f'\tLatios: {m2.get_optimal_moves_for_species(m2.pokemon_1.species)}\n'
                    f'\tAbsol: {m2.get_optimal_moves_for_species(m2.pokemon_2.species)}')

        # Damage Absol takes after n turns avg: 446
        # In the four pre-calculated, optimal, moves, Absol deals 446 damage on average per turn.
        # The first four moves are the expected damage after each move. As we assume Absol to use
        # SwordsDance in his first turn, Latios receives zero damage on turn one. In turn two,
        # Absol uses Knockoff, dealing 446 damage to Latios
        # In the fifth move, we expect Latios to have taken the damage of the first four turns,
        # plus the average damage of the four turns for the fifth turn
        assert m2.get_expected_damage_after_turns('latios', 1) == 0
        assert m2.get_expected_damage_after_turns('latios', 2) == 595
        assert m2.get_expected_damage_after_turns('latios', 3) == 1190
        assert m2.get_expected_damage_after_turns('latios', 4) == 1785
        assert m2.get_expected_damage_after_turns('latios', 5) == 2231

        # To make minmax easier, this method accepts less than one turn for input
        # This occurs, if both Pokemon can defeat the enemy in the first turn.
        assert m1.get_expected_damage_after_turns('charizard', 0) == 0
        assert m1.get_expected_damage_after_turns('charizard', -1) == 0
        assert m1.get_expected_damage_after_turns('charizard', -10) == 0

    def test_expected_turns_until_faint(self):
        matchup_creator = MatchupCreator(team_length=3, moves_depth=4)
        matchups = matchup_creator.get_test_matchups()

        m1: PokemonMatchup = [m for m in matchups if m.is_battle_between('charizard', 'roserade')][0]
        m2: PokemonMatchup = [m for m in matchups if m.is_battle_between('salamence', 'garchomp')][0]

        # Charizard vs Roserade
        assert m1.expected_turns_until_faint('charizard') == 3
        assert m1.expected_turns_until_faint('roserade') == 2

        # Both Pokemon can kill each other in the first turn
        assert m2.expected_turns_until_faint('salamence') == 1
        assert m2.expected_turns_until_faint('garchomp') == 1
