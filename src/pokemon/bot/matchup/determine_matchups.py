import copy
import itertools
from typing import Dict, List, Optional

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon

from pokemon.bot.matchup.field.field_side import FieldSide
from pokemon.bot.matchup.field.field_state import FieldState
from pokemon.bot.matchup.field.field_terrain import FieldTerrain
from pokemon.bot.matchup.field.field_weather import FieldWeather
from pokemon.bot.matchup.move_result import MoveResult
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.pokemon.config import MATCHUP_MOVES_DEPTH
from src.pokemon.data_handling.util.pokemon_creation import build_from_pokemon, pokemon_from_build


def determine_matchups(battle: AbstractBattle, enemy_builds: Dict[str, PokemonBuild]) -> PokemonMatchup:
    """Returns the matchups for all enemy Pokemon
    # TODO: This has to look farther in the future and include current state of the Pokemon
    """

    matchups = {}

    damage_calculator = DamageCalculator()

    own_pokemon: List[Pokemon] = battle.available_switches + [battle.active_pokemon] \
        if battle.active_pokemon is not None else []
    enemy_pokemon = [battle.opponent_team[p] for p in battle.opponent_team if not battle.opponent_team[p].fainted]

    # Determining checks and counter for each known enemy
    for enemy in enemy_pokemon:
        for member in own_pokemon:

            enemy_possible_moves = enemy_builds[enemy.species].get_most_likely_moves()

            # TODO: Create method that creates PokemonBuild from Pokemon
            member_build = build_from_pokemon(member)

            # Determining our optimal moves
            own_optimal_moves = get_optimal_moves(
                member_build,
                enemy_builds[enemy.species],
                member.moves,
                MATCHUP_MOVES_DEPTH,
                damage_calculator
            )

            # Calculating expected damage for check and counter
            own_expected_damage = sum(map(lambda x: x[1], own_optimal_moves))
            own_expected_damage_biggest_removed = sorted(own_optimal_moves, key=lambda x: x[1], reverse=True)[1:]
            own_expected_damage_check = sum(map(lambda x: x[1], own_expected_damage_biggest_removed))

            # Determining enemy optimal moves
            enemy_optimal_moves = get_optimal_moves(
                enemy_builds[enemy.species],
                member_build,
                enemy_possible_moves,
                MATCHUP_MOVES_DEPTH,
                damage_calculator)
            # Calculating enemy expected damage
            enemy_expected_damage = sum(map(lambda x: x[1], enemy_optimal_moves))

            ####################################################################
            # Counter                                                          #
            ####################################################################
            # A Pokémon is a *Counter* if it's stronger when switched in after #
            #   a faint.                                                       #
            ####################################################################
            # Check                                                            #
            ####################################################################
            # A Pokémon is a *Check* if it's stronger even when having to tank #
            #   one additional hit                                             #
            ####################################################################
            # Determining what Pokémon is *stronger*                           #
            ####################################################################
            # If the one Pokémon looses a bigger fraction of it's total health #
            #   it's considered to be weaker than the enemy                    #
            ####################################################################

            enemy_total_hp = enemy_builds[enemy.species].get_most_likely_stats()["hp"]

            damage_taken_fraction = enemy_expected_damage / member_build.get_most_likely_stats()["hp"]
            damage_given_fraction_counter = own_expected_damage / enemy_total_hp
            damage_given_fraction_check = own_expected_damage_check / enemy_total_hp

            # Checking if our Pokémon is a check or a counter to the enemy
            is_counter = damage_taken_fraction < damage_given_fraction_counter
            is_check = damage_taken_fraction < damage_given_fraction_check

            # Creating new entry for the given Pokémon if not already present
            if enemy.species not in matchups.keys():
                matchups[enemy.species] = {"checks": [], "counter": []}

            if is_check:
                matchups[enemy.species]["checks"].append(member.species)
            # print(f"{member.species} is check against {enemy.species}: {is_check}")

            if is_counter:
                matchups[enemy.species]["counter"].append(member.species)
            # print(f"{member.species} is counter against {enemy.species}: {is_counter}")

    # print(f"\n\nMatchups: {json.dumps(matchups, indent=4, sort_keys=True)}")

    # damage_calculator._cli_tool.kill()

    raise NotImplementedError('This has to return a PokemonMatchup')


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

        attacker_copy = copy.deepcopy(attacker_pokemon)
        defender_copy = copy.deepcopy(defender_pokemon)

        # Making all moves
        for current_move in combination:

            current_move = Move(current_move)

            # Calculating expected damage after these 3 moves
            res = damage_calculator.calculate_damage(
                attacker_build,
                defender_build,
                current_move,
                attacker_pokemon=attacker_copy,
                defender_pokemon=defender_copy,
                field=field_state)

            # Status changes
            attacker_copy.status = res.new_status_attacker
            defender_copy.status = res.new_status_defender

            # TODO: Include Moves that increase / decrease the stats of the enemy

            # Stat changes
            if current_move.boosts is not None:
                if current_move.target == 'allySide' or current_move.target == 'self':
                    for boost in current_move.boosts.keys():
                        attacker_copy.boosts[boost] += current_move.boosts[boost]

            if current_move.self_boost is not None:
                for boost in current_move.self_boost.keys():
                    attacker_copy.boosts[boost] += current_move.self_boost[boost]
            current_moves.append(res)

        # If the current combination is better than the best known combination
        current_expected_damage = sum([x.get_average_damage() for x in current_moves])

        if current_expected_damage >= best_move_expected_damage:
            best_moves = current_moves
            best_move_expected_damage = current_expected_damage

    print(f"Optimal moves for {attacker_build.species} vs {defender_build.species}:")
    print('\t' + '\t'.join([f'{res.move} ({res.get_average_damage()})' for res in best_moves])
          + f'\tTotal: ({best_move_expected_damage})')
    assert len(best_moves) == depth
    return best_moves
