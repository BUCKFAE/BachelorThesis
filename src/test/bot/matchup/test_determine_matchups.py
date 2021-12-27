import unittest

from poke_env.environment.battle import Battle

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.matchup.determine_matchups import determine_matchups, get_optimal_moves
from src.pokemon.data_handling.util.pokemon_creation import load_pokemon_from_file, load_build_from_file


class TestDetermineMatchup(unittest.TestCase):

    def test_determine_matchup(self):
        battle = Battle('test_battle_tag', 'buckfae', None, False)

        # Creating teams
        names_team_p1 = ["charizard", "salamence", "kyogre"]
        names_team_p2 = ["roserade", "luxray", "garchomp"]

        pokemon_p1 = [load_pokemon_from_file(p) for p in names_team_p1]

        pokemon_p2 = [load_pokemon_from_file(p) for p in names_team_p2]
        builds_p2 = [load_build_from_file(p) for p in names_team_p2]

        battle._available_switches = pokemon_p1
        battle._active_pokemon = pokemon_p1[0]

        battle._opponent_team = {names_team_p2[p]: pokemon_p2[p] for p in range(len(names_team_p2))}

        matchups = determine_matchups(battle, {names_team_p2[p]: builds_p2[p] for p in range(len(names_team_p2))})

        # Getting Checks and counter
        for matchup in matchups:
            p1 = matchup.pokemon_1.species
            p2 = matchup.pokemon_2.species
            logger.info(f'{p1} checks {p2}: {matchup.is_check(p1, p2)}')
            logger.info(f'{p2} checks {p1}: {matchup.is_check(p2, p1)}')
            logger.info(f'{p1} counters {p2}: {matchup.is_counter(p1, p2)}')
            logger.info(f'{p2} counters {p1}: {matchup.is_counter(p2, p1)}')

    def _test_get_optimal_moves(self):

        build1 = load_build_from_file("absol")
        build2 = load_build_from_file("latios")

        print(f'\n\nMoves of {build1.species}: {build1.get_most_likely_moves()}')
        print(f'Moves of {build2.species}: {build2.get_most_likely_moves()}')

        d = DamageCalculator()

        optimal_moves_absol = get_optimal_moves(build1, build2, build1.get_most_likely_moves(), 4, d)
        optimal_moves_latios = get_optimal_moves(build2, build1, build2.get_most_likely_moves(), 4, d)




if __name__ == "__main__":
    unittest.main()
