import datetime
from typing import Dict

from poke_env.environment.abstract_battle import AbstractBattle

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.pokemon.bot.minimax.min_max_node import MinMaxNode


def create_game_plan(battle: AbstractBattle, enemy_builds: Dict[str, PokemonBuild]):
    logger.info('Creating matchups for game plan')
    matchups = determine_matchups(battle, enemy_builds)
    logger.info('Finished creating matchups')

    remaining_hp_team_1 = {p.species: p.current_hp for p in battle.team.values()}
    remaining_hp_team_2 = {p.species: p.current_hp for p in battle.opponent_team.values()}

    root = MinMaxNode(
        battle.active_pokemon.species,
        battle.opponent_active_pokemon.species,
        remaining_hp_team_1,
        remaining_hp_team_2,
        matchups)

    start_time = datetime.datetime.now()
    root.build_tree_below_node()

    end_time = datetime.datetime.now()
    logger.info(f"Building tree took: {(end_time - start_time)}")
    logger.info('Finished getting matchups')

    return root
