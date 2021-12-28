import itertools
from typing import Dict, List, Optional

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.field.field_side import FieldSide
from src.pokemon.bot.matchup.field.field_state import FieldState
from src.pokemon.bot.matchup.field.field_terrain import FieldTerrain
from src.pokemon.bot.matchup.field.field_weather import FieldWeather
from src.pokemon.bot.matchup.move_result import MoveResult
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.pokemon.config import MATCHUP_MOVES_DEPTH
from src.pokemon.data_handling.util.pokemon_creation import build_from_pokemon, pokemon_from_build, clone_pokemon


def determine_matchups(battle: AbstractBattle,
                       enemy_builds: Dict[str, PokemonBuild]) -> List[PokemonMatchup]:
    """Returns the matchups for all enemy Pokemon"""

    # Stores all matchups
    matchups = []

    damage_calculator = DamageCalculator()

    # Getting both teams
    own_pokemon = battle.available_switches + ([battle.active_pokemon]
                                               if battle.active_pokemon is not None else [])
    enemy_pokemon = [battle.opponent_team[p] for p in battle.opponent_team if not battle.opponent_team[p].fainted]

    logger.info(f'Determining matchups:\n\t{"-".join([s.species for s in own_pokemon])}'
                f' -- {"-".join([s.species for s in enemy_pokemon])}')

    # Determining checks and counter for each known enemy
    for enemy in enemy_pokemon:
        for member in own_pokemon:

            member_build = build_from_pokemon(member)

            # Determining our optimal moves
            own_optimal_moves = get_optimal_moves(
                attacker_build=member_build,
                defender_build=enemy_builds[enemy.species],
                possible_moves=member_build.get_most_likely_moves(),
                depth=MATCHUP_MOVES_DEPTH,
                damage_calculator=damage_calculator,
                attacker_pokemon=member,
                defender_pokemon=enemy
            )

            enemy_optimal_moves = get_optimal_moves(
                attacker_build=enemy_builds[enemy.species],
                defender_build=member_build,
                possible_moves=enemy_builds[enemy.species].get_most_likely_moves(),
                depth=MATCHUP_MOVES_DEPTH,
                damage_calculator=damage_calculator,
                attacker_pokemon=enemy,
                defender_pokemon=member
            )

            matchup = PokemonMatchup(
                build_p1=member_build,
                pokemon_1=member,
                build_p2=enemy_builds[enemy.species],
                pokemon_2=enemy,
                optimal_moves_p1=own_optimal_moves,
                optimal_moves_p2=enemy_optimal_moves
            )

            matchups.append(matchup)

    return matchups

def get_optimal_moves(
        attacker_build: PokemonBuild,
        defender_build: PokemonBuild,
        possible_moves: List[str],
        depth: int,
        damage_calculator: DamageCalculator,
        field_state: Optional[FieldState] = None,
        attacker_pokemon: Optional[Pokemon] = None,
        defender_pokemon: Optional[Pokemon] = None):
    # All possible move combinations
    combinations = itertools.product(possible_moves, repeat=depth)

    # print(f"Getting optimal moves for {attacker.species} vs {defender.species}")

    if attacker_pokemon is None:
        attacker_pokemon = pokemon_from_build(attacker_build)

    if defender_pokemon is None:
        defender_pokemon = pokemon_from_build(defender_build)

    # Storing the best move combination
    best_moves = List[MoveResult]
    best_move_expected_damage = -1

    for combination in combinations:
        #print(f"{combination=}")
        current_moves = []

        # Creating field at the start if needed
        if field_state is None:
            field_side_p1 = FieldSide()
            field_side_p2 = FieldSide()
            field_state = FieldState(
                FieldTerrain.DEFAULT,
                FieldWeather.DEFAULT,
                field_side_p1,
                field_side_p2
            )

        # Here the HP percentage is also adjusted
        attacker_copy = clone_pokemon(attacker_pokemon, attacker_build)
        defender_copy = clone_pokemon(defender_pokemon, defender_build)

        attacker_copy.item = ''
        defender_copy.item = ''

        assert attacker_pokemon.boosts == attacker_copy.boosts
        assert defender_pokemon.boosts == defender_copy.boosts

        if attacker_pokemon.base_stats != attacker_copy.base_stats:
            logger.critical('Attacker had wrong stats')


        if defender_pokemon.base_stats != defender_pokemon.base_stats:
            logger.critical('Defender had wrong stats')

        # Making all moves
        for current_move in combination:
            #print(f'{current_move=}')
            current_move = Move(current_move)

            # Calculating expected damage after these 3 moves
            res = damage_calculator.calculate_damage(
                attacker_build,
                defender_build,
                current_move,
                attacker_pokemon=attacker_copy,
                defender_pokemon=defender_copy,
                field=None)

            # Status changes
            attacker_copy.status = res.new_status_attacker
            defender_copy.status = res.new_status_defender

            # TODO: Include Moves that increase / decrease the stats of the enemy

            # Stat changes
            if current_move.boosts is not None:
                if current_move.target == 'allySide' or current_move.target == 'self':
                    for boost in current_move.boosts.keys():
                        attacker_copy.boosts[boost] += current_move.boosts[boost]
                        if attacker_copy.boosts[boost] > 6:
                            attacker_copy.boosts[boost] = 6
                        if attacker_copy.boosts[boost] < -6:
                            attacker_copy.boosts[boost] = -6

            if current_move.self_boost is not None:
                for boost in current_move.self_boost.keys():
                    attacker_copy.boosts[boost] += current_move.self_boost[boost]
                    if attacker_copy.boosts[boost] > 6:
                        attacker_copy.boosts[boost] = 6
                    if attacker_copy.boosts[boost] < -6:
                        attacker_copy.boosts[boost] = -6

            current_moves.append(res)

        # If the current combination is better than the best known combination
        current_expected_damage = sum([x.get_average_damage() for x in current_moves])

        if current_expected_damage >= best_move_expected_damage:
            best_moves = current_moves
            best_move_expected_damage = current_expected_damage

    #logger.info(f"Optimal moves for {attacker_build.species} vs {defender_build.species}:" +
    #            '\t' + '\t'.join([f'{res.move} ({res.get_average_damage()})' for res in best_moves])
    #            + f'\tTotal: ({best_move_expected_damage})')
    assert len(best_moves) == depth
    return best_moves
