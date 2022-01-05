import datetime
from typing import Dict, List

from poke_env.environment.abstract_battle import AbstractBattle

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.pokemon.bot.minimax.min_max_node import MinMaxNode


def create_game_plan(battle: AbstractBattle, enemy_builds: Dict[str, PokemonBuild],
                     matchups: List[PokemonMatchup] = None) -> MinMaxNode:

    if matchups is None:
        matchups = determine_matchups(battle, enemy_builds)

    remaining_hp_team_1 = {p.species: p.current_hp for p in battle.team.values() if not p.fainted}
    remaining_hp_team_2 = {p.species: p.current_hp for p in battle.opponent_team.values() if not p.fainted or p.active}

    # Active pokemon not fainted: Build all trees
    if battle.active_pokemon.fainted:
        logger.info(f'Active pokemon fainted')
        logger.info(f'{remaining_hp_team_1=}')
        logger.info(f'{remaining_hp_team_2=}')
        logger.info(f'{battle.available_switches=}')
        logger.info(f'{battle.active_pokemon.fainted}')
        best_node = None
        best_score = None
        for possible_switch in battle.available_switches:
            node = MinMaxNode(
                possible_switch.species,
                battle.opponent_active_pokemon.species,
                remaining_hp_team_1,
                remaining_hp_team_2,
                matchups
            )
            node.build_tree_below_node()
            score = node.evaluate_node()

            if best_node is None or score > best_score:
                best_node = node
                best_score = score
        return best_node

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
