import datetime
import unittest

from poke_env.environment.battle import Battle

from src.pokemon import logger
from src.pokemon.bot.minimax.min_max import create_game_plan
from src.pokemon.data_handling.util.pokemon_creation import load_pokemon_from_file, load_build_from_file, clone_pokemon


class TestMinMaxPerformance(unittest.TestCase):

    def test_min_max_performance(self):
        """
        Tests how much time the min max takes
        """

        logger.info('Testing MinMax performance!')

        battle = Battle('test_battle_tag', 'buckfae', None, False)

        names_team_p1 = ['charizard', 'salamence', 'kyogre', 'pikachu', 'gastrodon', 'dialga']
        names_team_p2 = ['roserade', 'luxray', 'garchomp', 'xatu', 'yveltal', 'zekrom']

        pokemon_p1 = [clone_pokemon(load_pokemon_from_file(p), load_build_from_file(p)) for p in names_team_p1]
        pokemon_p1[0]._active = True
        pokemon_p2 = [clone_pokemon(load_pokemon_from_file(p), load_build_from_file(p)) for p in names_team_p2]
        pokemon_p2[0]._active = True
        builds_p2 = [load_build_from_file(p) for p in names_team_p2]

        # Setting up the battle
        battle._available_switches = pokemon_p1
        battle._team = {f'p1: {p.species.capitalize()}': p for p in pokemon_p1}
        battle._opponent_team = {names_team_p2[p]: pokemon_p2[p] for p in range(len(names_team_p2))}
        enemy_builds = {names_team_p2[p]: builds_p2[p] for p in range(len(names_team_p2))}


        # Creating game plan
        plan = create_game_plan(battle, enemy_builds)

        logger.info('Done')
