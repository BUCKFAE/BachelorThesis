import itertools
import sys
from typing import Dict, List, Optional

from poke_env.environment import status
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.move_category import MoveCategory
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
                       enemy_builds: Dict[str, PokemonBuild], depth: int = MATCHUP_MOVES_DEPTH,
                       is_early_game: bool = False,
                       existing_matchups: Optional[List[PokemonMatchup]] = None,
                       matchups_to_update: Optional[List[str]] = None) -> List[PokemonMatchup]:
    """Returns the matchups for all enemy Pokemon"""

    # Stores all matchups
    matchups = [] if existing_matchups is None else existing_matchups

    # TODO: This fails to check if a Pokémon is dead and tries to send out a fainted Pokémon

    damage_calculator = DamageCalculator()

    # Getting both teams
    own_pokemon = [p for p in battle.team.values() if not p.fainted]
    enemy_pokemon = [battle.opponent_team[p] for p in battle.opponent_team if not battle.opponent_team[p].fainted]

    logger.info(f'Determining matchups:\n\t{"-".join([s.species for s in own_pokemon])}'
                f' -- {"-".join([s.species for s in enemy_pokemon])}')

    # Determining checks and counter for each known enemy
    for enemy in enemy_pokemon:
        for member in own_pokemon:

            # Checking if we already know this matchup
            current_matchup = [i for i in range(len(matchups))
                               if matchups[i].pokemon_1.species == member.species
                               and matchups[i].pokemon_2.species == enemy.species]

            assert len(current_matchup) <= 1

            replace_index = -1

            # If we already know the matchup, we store the index of the matchup to update.
            if matchups_to_update is not None and len(current_matchup) == 1:
                if matchups[current_matchup[0]].pokemon_2.species in matchups_to_update:
                    replace_index = current_matchup[0]
                else:
                    continue

            member_build = build_from_pokemon(member)

            # Determining our optimal moves
            own_optimal_moves = get_optimal_moves(
                attacker_build=member_build,
                defender_build=enemy_builds[enemy.species],
                possible_moves=member_build.get_most_likely_moves(),
                depth=depth,
                damage_calculator=damage_calculator,
                attacker_pokemon=member,
                defender_pokemon=enemy,
                is_early_game=is_early_game
            )

            enemy_optimal_moves = get_optimal_moves(
                attacker_build=enemy_builds[enemy.species],
                defender_build=member_build,
                possible_moves=enemy_builds[enemy.species].get_most_likely_moves(),
                depth=depth,
                damage_calculator=damage_calculator,
                attacker_pokemon=enemy,
                defender_pokemon=member,
                is_early_game=is_early_game,
                use_no_drawback=False
            )

            matchup = PokemonMatchup(
                build_p1=member_build,
                pokemon_1=member,
                build_p2=enemy_builds[enemy.species],
                pokemon_2=enemy,
                optimal_moves_p1=own_optimal_moves,
                optimal_moves_p2=enemy_optimal_moves
            )

            # Appending matchup if it is new, replacing old matchup if existing
            if replace_index == -1:
                matchups.append(matchup)
            else:
                matchups[replace_index] = matchup

    matchups = [m for m in matchups if not m.pokemon_1.fainted and not m.pokemon_2.fainted]

    return matchups


def get_optimal_moves(
        attacker_build: PokemonBuild,
        defender_build: PokemonBuild,
        possible_moves: List[str],
        depth: int,
        damage_calculator: DamageCalculator,
        field_state: Optional[FieldState] = None,
        attacker_pokemon: Optional[Pokemon] = None,
        defender_pokemon: Optional[Pokemon] = None,
        is_early_game: bool = False,
        use_no_drawback: bool = True) -> List[MoveResult]:
    """
    Calculates the optimal moves of the attacker against the defender
    :param attacker_build: The build of the attacking Pokemon
    :param defender_build: The build of the defending Pokemon
    :param possible_moves: The Moves the attacking Pokemon can use
    :param depth: How many turns to look into the future
    :param damage_calculator: The damage calculator instance to use. This is passed as the calculator
        takes some time to set up for the first time
    :param field_state: The current state of the field
    :param attacker_pokemon: The Pokemon attacking
    :param defender_pokemon: The Pokemon getting attacked
    :param is_early_game: We won't boost in the early game
    """

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
    best_moves_turns_to_kill = 1000

    knows_no_drawback_moves = False

    for combination in combinations:

        # Skipping boosting combination in early game
        if is_early_game:
            if any([Move(c).boosts and Move(c).target in ['allySide', 'self'] for c in combination]):
                continue

        # Only boosting once
        if len([c for c in combination if Move(c).boosts is not None and Move(c).target in ['allySide', 'self']]) > 1:
            continue

        # Not boosting if pokemon is already boosted
        if attacker_pokemon.boosts:
            if any([Move(c).boosts is not None and Move(c).target in ['allySide', 'self'] for c in combination]):
                continue

        # Not using explosion if we are above 25% hp
        if any([Move(c).id == 'explosion' for c in combination]) and attacker_pokemon.current_hp_fraction > 0.25:
            continue

        # print(f"{combination=}")
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

        assert attacker_pokemon.boosts == attacker_copy.boosts
        assert defender_pokemon.boosts == defender_copy.boosts

        if attacker_pokemon.base_stats != attacker_copy.base_stats:
            logger.critical('Attacker had wrong stats')

        if defender_pokemon.base_stats != defender_pokemon.base_stats:
            logger.critical('Defender had wrong stats')

        # Making all moves
        for current_move in list(combination):
            # print(f'{current_move=}')
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

        # Calculating the damage the attacker takes
        defender_damage_taken = sum([x.get_average_damage() * Move(x.move).accuracy for x in current_moves])

        defender_hp = defender_pokemon.current_hp if defender_pokemon is not None \
            else defender_build.get_most_likely_stats()["hp"]

        # We haven't found a combination to kill yet, picking the one that deals the most amount of damage
        if defender_damage_taken < defender_hp:
            if best_moves_turns_to_kill == 1000:

                # Using no drawback move
                first_is_no_drawback = is_no_drawback_move(Move(combination[0]), defender_pokemon, attacker_pokemon)

                if not use_no_drawback:
                    first_is_no_drawback = False

                if first_is_no_drawback:
                    # Not the first no-drawback-move. Picking combination that deals more damage
                    if knows_no_drawback_moves:
                        if defender_damage_taken >= best_move_expected_damage:
                            best_moves = current_moves
                            best_move_expected_damage = defender_damage_taken
                    else:
                        # This is the first no drawback move. Using this combination as new best
                        best_moves = current_moves
                        best_move_expected_damage = defender_damage_taken
                    knows_no_drawback_moves = True

                elif defender_damage_taken >= best_move_expected_damage:
                    # Pokemon doesn't know any no drawback moves, dealing the most amount of damage possible
                    best_moves = current_moves
                    best_move_expected_damage = defender_damage_taken

        else:
            to_kill = _get_turns_until_faint_from_moves(defender_hp, current_moves)
            if to_kill < best_moves_turns_to_kill or \
                    (to_kill == best_moves_turns_to_kill and defender_damage_taken >= best_move_expected_damage):
                best_moves = current_moves
                best_move_expected_damage = defender_damage_taken
                best_moves_turns_to_kill = to_kill

        # logger.info(f"Optimal moves for {attacker_build.species} vs {defender_build.species}:" +
    #            '\t' + '\t'.join([f'{res.move} ({res.get_average_damage()})' for res in best_moves])
    #            + f'\tTotal: ({best_move_expected_damage})')

    return best_moves


def is_no_drawback_move(move: Move, defender: Pokemon, attacker: Pokemon) -> bool:
    """Determines if the given move is a no drawback move against the given enemy

    A move is a has no drawback if:
    - We add a status to the enemy
    """

    # If the move applies a status to the enemy Pokemon
    if move.status is not None:

        if move.category != MoveCategory.STATUS:
            print('oof')

        # If we kill ourself
        if move.self_destruct and attacker.current_hp_fraction > 0.3:
            return False

        # If the enemy is already affected by a status we won't use the move as status can't be stacked
        if defender.status is not None:
            return False

        return True

    return False


def _get_turns_until_faint_from_moves(hp: int, attacks: List[MoveResult]) -> int:
    damage_taken = 0
    turn = 0
    while damage_taken < hp:
        turn += 1
        damage_taken += attacks[turn - 1].get_average_damage() * Move(attacks[turn - 1].move).accuracy
    return turn
