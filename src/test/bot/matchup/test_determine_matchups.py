import unittest

from poke_env.environment.battle import Battle

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.matchup.determine_matchups import determine_matchups, get_optimal_moves
from src.pokemon.data_handling.util.pokemon_creation import load_pokemon_from_file, load_build_from_file
from src.test.bot.matchup.matchup_creator import MatchupCreator


class TestDetermineMatchup(unittest.TestCase):

    def test_determine_matchup(self):

        matchup_creator = MatchupCreator()

        # Getting Checks and counter
        for matchup in matchup_creator.get_test_matchups():
            p1 = matchup.pokemon_1.species
            p2 = matchup.pokemon_2.species
            logger.info(f'{p1} checks {p2}: {matchup.is_check(p1, p2)}')
            logger.info(f'{p2} checks {p1}: {matchup.is_check(p2, p1)}')
            logger.info(f'{p1} counters {p2}: {matchup.is_counter(p1, p2)}')
            logger.info(f'{p2} counters {p1}: {matchup.is_counter(p2, p1)}')

    def test_get_optimal_moves(self):

        build1 = load_build_from_file("absol")
        build2 = load_build_from_file("latios")

        print(f'\n\nMoves of {build1.species}: {build1.get_most_likely_moves()}')
        print(f'Moves of {build2.species}: {build2.get_most_likely_moves()}')

        d = DamageCalculator()

        for is_early_game in [True, False]:
            optimal_moves_absol = get_optimal_moves(
                build1, build2, build1.get_most_likely_moves(), 4, d,
                is_early_game=is_early_game)
            optimal_moves_latios = get_optimal_moves(
                build2, build1, build2.get_most_likely_moves(), 4, d,
                is_early_game=is_early_game)

            logger.info(f'Early Game: {is_early_game}\n{optimal_moves_absol=}')
            logger.info(f'Early Game: {is_early_game}\n{optimal_moves_latios=}')





if __name__ == "__main__":
    unittest.main()
