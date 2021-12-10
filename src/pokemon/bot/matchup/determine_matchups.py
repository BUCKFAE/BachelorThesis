import sys
import itertools
from typing import Dict, List

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.pokemon_gender import PokemonGender

from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator, extract_evs_ivs_from_build, \
    get_total_stat
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild


def determine_matchups(battle: AbstractBattle, enemy_builds: Dict[str, PokemonBuild]):
    """Returns the matchups for all enemy Pokémon
    Dict {Pokémon: ([Checks], [Counter])}
    """

    matchups = {}

    # TODO: This should be a factory
    print(f"Starting Damage calculator")
    damage_calculator = DamageCalculator()
    print(f"Finished Starting Damage calculator")

    own_pokemon: List[Pokemon] = battle.available_switches
    enemy_pokemon = [battle.opponent_team[p] for p in battle.opponent_team if not battle.opponent_team[p].fainted]

    print(f"Pokemon p1: {own_pokemon}")
    print(f"Pokemon p2: {enemy_pokemon}\n\n")

    # Determining checks and counter for each known enemy
    for enemy in enemy_pokemon:
        for member in own_pokemon:

            # TODO: Simulation can be skipped in many cases, e.g. clear type advantage

            print(f"\n\nGetting matchup: {member.species} vs. {enemy.species}")

            enemy_possible_moves = enemy_builds[enemy.species].get_most_likely_moves()
            print(f"{enemy.species} possible moves: {enemy_possible_moves}")
            print(f"{member.species} possible moves: {[str(move) for move in member.moves]}")

            # TODO: Create method that creates PokemonBuild from Pokemon
            member_build = PokemonBuild(
                member.species,
                member.level,
                "MALE" if member.gender == PokemonGender.MALE
                else ("FEMALE" if member.gender == PokemonGender.FEMALE else "NEUTRAL"),
                member.item,
                member.ability)
            member_build._possible_builds = [(
                {"ability": member.ability,
                 "stats": {**member.stats, **{"hp": member_build.get_most_likely_stats()["hp"]}},
                 "gender": "MALE" if member.gender == PokemonGender.MALE
                 else ("FEMALE" if member.gender == PokemonGender.FEMALE else "NEUTRAL"),
                 "item": member.item,
                 "level": member.item,
                 "moves": "|".join(member.moves)}, 1)]

            # Determining our optimal moves
            own_optimal_moves = get_optimal_moves(
                member_build,
                enemy_builds[enemy.species],
                enemy_possible_moves,
                3,
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
                member.moves,
                3,
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

            # TODO: Enemy HP Stat is always 100!

            enemy_total_hp = enemy_builds[enemy.species].get_most_likely_stats()["hp"]

            enemy_damage_fraction = enemy_expected_damage / member_build.get_most_likely_stats()["hp"]
            own_damage_fraction_counter = own_expected_damage / enemy_total_hp
            own_damage_fraction_check = own_expected_damage_check / enemy_total_hp

            # Checking if our Pokémon is a check or a counter to the enemy
            is_counter = own_damage_fraction_counter < enemy_damage_fraction
            is_check = own_damage_fraction_check < enemy_damage_fraction

            # Creating new entry for the given Pokémon if not already present
            if enemy.species not in matchups.keys():
                matchups[enemy.species] = {"checks": [], "counter": []}

            if is_check:
                matchups[enemy.species]["checks"].append(member.species)
            print(f"{member.species} is check against {enemy.species}: {is_check}")

            if is_counter:
                matchups[enemy.species]["counter"].append(member.species)
            print(f"{member.species} is counter against {enemy.species}: {is_counter}")

    print(f"Matchups: {matchups}")

    return matchups


def get_optimal_moves(
        attacker: PokemonBuild,
        defender: PokemonBuild,
        possible_moves: List[str],
        depth: int,
        damage_calculator: DamageCalculator):
    # All possible move combinations
    combinations = itertools.product(possible_moves, repeat=depth)

    # print(f"Getting optimal moves for {attacker.species} vs {defender.species}")

    # Storing the best move combination
    best_moves = [(None, -1)]

    for combination in combinations:
        current_moves = []

        # TODO: This should include field effects and stat changes, don't 3x draco meteor!

        # Making all moves
        for current_move in combination:
            # Calculating expected damage after these 3 moves
            res = damage_calculator.calculate_damage(
                attacker,
                defender,
                Move(current_move),
                None,
                None)
            expected_damage_current_move = sum(res) / len(res)
            current_moves.append((current_move, expected_damage_current_move))

        # If the current combination is better than the best known combination
        current_expected_damage = sum(map(lambda x: x[1], current_moves))
        best_expected_damage = sum(map(lambda x: x[1], best_moves))

        if current_expected_damage >= best_expected_damage:
            best_moves = current_moves

    print(f"Optimal moves: {best_moves}")

    assert len(best_moves) == depth
    return best_moves
