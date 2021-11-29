import sys
import itertools
from typing import Dict, List

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.pokemon import Pokemon

from src.pokemon.bot.pokemon_build import PokemonBuild


def determine_matchups(battle: AbstractBattle, enemy_builds: Dict[str, PokemonBuild]):
    own_pokemon: List[Pokemon] = battle.available_switches
    enemy_pokemon = [battle.opponent_team[p] for p in battle.opponent_team if not battle.opponent_team[p].fainted]

    print(f"Pokemon p1: {own_pokemon}")
    print(f"Pokemon p2: {enemy_pokemon}")

    for enemy in enemy_pokemon:
        for member in own_pokemon:

            print(f"Getting matchup: {member.species} vs. {enemy.species}")

            enemy_possible_moves = enemy_builds[enemy.species].possible_moves.keys()
            print(f"Enemy possible moves: {enemy_possible_moves}")

            enemy_actions = itertools.product(enemy_possible_moves, repeat=2)

            # All possible enemy moves
            for enemy_moves in enemy_actions:
                # All possible reactions
                for own_actions in itertools.product(member.moves, repeat=2):
                    print("Enemy actions:\t{}".format("\t".join(enemy_moves)))
                    print("Own actions:\t{}".format("\t".join(own_actions)))

                    own_hp = member.current_hp
                    enemy_hp = enemy.current_hp



            sys.exit(0)

    pass