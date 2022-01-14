import datetime
import unittest

from poke_env.environment.battle import Battle

from src.pokemon import logger
from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.bot.minimax.min_max import create_game_plan
from src.pokemon.bot.minimax.min_max_node import MinMaxNode
from src.pokemon.bot.minimax.visualize_tree import visualize_tree
from src.pokemon.data_handling.util.pokemon_creation import load_pokemon_from_file, load_build_from_file, clone_pokemon


class TestMinMaxPerformance(unittest.TestCase):

    def test_min_max_performance(self):
        """
        Tests how much time the min max takes
        """

        logger.info('Testing MinMax performance!')

        battle = Battle('test_battle_tag', 'buckfae', None, False)

        names_team_p1 = ['roserade', 'salamence', 'kyogre']
        names_team_p2 = ['charizard', 'luxray', 'garchomp']

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
        matchups = determine_matchups(battle, enemy_builds)

        remaining_hp_team_1 = {p.species: p.current_hp for p in battle.team.values() if not p.fainted}
        remaining_hp_team_2 = {p.species: p.current_hp for p in battle.opponent_team.values() if
                               not p.fainted or p.active}

        plan = MinMaxNode(
            names_team_p1[0],
            names_team_p2[0],
            remaining_hp_team_1,
            remaining_hp_team_2,
            matchups
        )
        plan.build_tree_below_node()

        logger.info('Finished creating game plan')

        # Testing visualization
        dot = visualize_tree(plan)
        logger.info('Finished other')
        dot.render(view=True, format='png')
