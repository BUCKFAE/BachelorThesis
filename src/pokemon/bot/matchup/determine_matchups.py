import sys
import itertools
from typing import Dict, List

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.pokemon_gender import PokemonGender

from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild


def determine_matchups(battle: AbstractBattle, enemy_builds: Dict[str, PokemonBuild]):
    # TODO: This should be a factory
    print(f"Starting Damage calculator")
    damage_calculator = DamageCalculator()
    print(f"Finished Starting Damage calculator")

    own_pokemon: List[Pokemon] = battle.available_switches
    enemy_pokemon = [battle.opponent_team[p] for p in battle.opponent_team if not battle.opponent_team[p].fainted]

    print(f"Pokemon p1: {own_pokemon}")
    print(f"Pokemon p2: {enemy_pokemon}\n\n")

    # Check:
    # If the expected maximum damage dealt by the enemy after n turns is smaller than the expected
    #   maximal damage after (n - 1) turns

    # Counter:
    # If the expected maximum damage dealt by the enemy after n turns is smaller than the expected
    #   maximal damage after n turns

    for enemy in enemy_pokemon:
        for member in own_pokemon:

            # TODO: Simulation can be skipped in many cases, e.g. clear type advantage

            print(f"Getting matchup: {member.species} vs. {enemy.species}")

            enemy_possible_moves = enemy_builds[enemy.species].get_most_likely_moves()
            print(f"Enemy possible moves: {enemy_possible_moves}")

            enemy_actions = itertools.product(enemy_possible_moves, repeat=3)

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
                 "stats": {**member.stats, **{"hp": member.max_hp}},
                 "gender": "MALE" if member.gender == PokemonGender.MALE
                 else ("FEMALE" if member.gender == PokemonGender.FEMALE else "NEUTRAL"),
                 "item": member.item,
                 "level": member.item,
                 "moves": "|".join(member.moves)}, 1)]

            optimal_enemy_moves = get_optimal_moves(
                member_build,
                enemy_builds[enemy.species],
                enemy_possible_moves,
                3
            )

            sys.exit(0)

            enemy_max_damage = -1
            enemy_best_combination = None
            member_max_damage = -1
            member_best_combination = None

            # All possible enemy moves
            for enemy_moves in enemy_actions:
                # print("Enemy actions:\t{}".format("\t".join(enemy_moves)))

                move_damages = 0
                for current_move in enemy_moves:
                    # TODO: Apply effects after move!

                    # Calculating expected damage after these 3 moves
                    res = damage_calculator.calculate_damage(
                        enemy_builds[enemy.species],
                        member_build,
                        Move(current_move),
                        None,
                        None)
                    print(res)
                    move_damages += sum(res) / len(res)

                # If the current move combination is better than the one we found
                if move_damages > enemy_max_damage:
                    enemy_max_damage = move_damages
                    enemy_best_combination = enemy_moves

            print(f"Enemy best move combination: {enemy_best_combination} ({enemy_max_damage})")

            # All possible reactions
            for own_actions in itertools.product(member.moves, repeat=3):
                # print("Own actions:\t{}".format("\t".join(own_actions)))

                move_damages = 0
                for current_move in own_actions:
                    # TODO: Apply effects after move!

                    # Calculating expected damage after these 3 moves
                    res = damage_calculator.calculate_damage(
                        member_build,
                        enemy_builds[enemy.species],
                        Move(current_move),
                        None,
                        None)
                    move_damages += sum(res) / len(res)

                # If the current move combination is better than the one we found
                if move_damages > member_max_damage:
                    member_max_damage = move_damages
                    member_best_combination = own_actions

            print(f"Enemy best move combination: {member_best_combination} ({member_max_damage})")

            sys.exit(0)


def get_optimal_moves(attacker: PokemonBuild, defender: PokemonBuild, possible_moves: List[str], depth: int):

    best_moves = [(None, -1)]

    assert len(best_moves) == depth
    return 2
