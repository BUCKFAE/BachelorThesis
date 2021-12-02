import sys
import itertools
from typing import Dict, List

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.pokemon import Pokemon
from progress.bar import IncrementalBar

from src.pokemon.bot.pokemon_build import PokemonBuild
from src.pokemon.replays.replay_loader import load_replays, replay_load_count
from src.pokemon.replays.util import convert_species_to_file_name


def load_matchups_from_replays():
    bar = IncrementalBar('Loading Replays:', max=replay_load_count)

    damage_per_turn = {}

    for batch in load_replays():
        for replay in batch:
            log = replay["log"]

            c = 0

            # Tracking the remaining hp of both pokemon
            # This is done as showdown only tells us how much hp is remaining
            # after a pokemon took damage, not how much damage was dealt.
            pokemon_p1_hp = 0
            pokemon_p1_name = ""
            pokemon_p2_hp = 0
            pokemon_p2_name = ""

            # Damage dealt this round
            # TODO: USE HP BEFORE THIS TURN
            total_damage_p1 = 0
            total_damage_p2 = 0

            for index, message in enumerate(log, start=1):

                print(f"\n\n{index:02d} -> {message}")

                # Switched to another pokemon
                if "|switch|" in message:
                    # Storing the hp of the active pokemon
                    if "p1a" in message:
                        pokemon_p1_hp = int(message.split("|")[-1].split("/")[0])
                        pokemon_p1_name = message.split("|")[2]
                        print(f"Switched to {pokemon_p1_name}: {pokemon_p1_hp}")
                    if "p2a" in message:
                        pokemon_p2_hp = int(message.split("|")[-1].split("/")[0])
                        pokemon_p2_name = message.split("|")[2]
                        print(f"Switched to {pokemon_p2_name}: {pokemon_p2_hp}")


                # TODO: track hp difference between rounds

                # Pokemon was healed
                if "|heal|" in message:
                    if "p1a" in message:
                        pokemon_p1_hp = int(message.split("|")[3].split("/"[0]))
                        print(f"Pokemon 1 is now at {pokemon_p1_hp} HP")
                    if "p2a" in message:
                        pokemon_p2_hp = int(message.split("|")[3].split("/"[0]))
                        print(f"Pokemon 2 is now at {pokemon_p2_hp} HP")

                # A turn ended, storing results
                if "|turn|" in message:
                    name1 = convert_species_to_file_name(pokemon_p1_name)
                    name2 = convert_species_to_file_name(pokemon_p2_name)

                    damage_per_turn[f"{name1}_vs_{name2}"] =  \
                        damage_per_turn.get(f"{name1}_vs_{name2}", 0) + total_damage_p2
                    damage_per_turn[f"{name2}_vs_{name1}"] =  \
                        damage_per_turn.get(f"{name2}_vs_{name1}", 0) + total_damage_p1


                # Continue if no move
                if "|move|" not in message:
                    continue

                # Getting attacker, move and target
                _, _, attacker, move, target = message.split("|")

                print(f"\t{attacker}: {move} -> {target}")

                print(f"\tHP: {pokemon_p1_hp} vs {pokemon_p2_hp}")



                effect = index
                while log[effect] != "|upkeep" and "|move|" not in log[effect]:

                    if "-damage" in log[effect]:

                        new_hp = int(log[effect].split("|")[3].split("/")[0]) if "|0" not in log[effect] else 0

                        print(f"New HP: {new_hp}")
                        # TODO: Add self damage
                        if "p1a" in log[effect]:
                            total_damage_p1 += pokemon_p1_hp - new_hp
                            pokemon_p1_hp = new_hp

                        if "p2a" in log[effect]:
                            total_damage_p2 += pokemon_p2_hp - new_hp
                            pokemon_p2_hp = new_hp

                    effect += 1

                print(f"\tDamage: {total_damage_p1} / {total_damage_p2}")

                # TODO: Fix pokemon names!

                # Stopping after few messages
                c += 1
                if c > 10:
                    break

            print(damage_per_turn)

            sys.exit(0)

            bar.next()

    bar.finish()


def determine_matchups(battle: AbstractBattle, enemy_builds: Dict[str, PokemonBuild]):
    own_pokemon: List[Pokemon] = battle.available_switches
    enemy_pokemon = [battle.opponent_team[p] for p in battle.opponent_team if not battle.opponent_team[p].fainted]

    print(f"Pokemon p1: {own_pokemon}")
    print(f"Pokemon p2: {enemy_pokemon}")

    for enemy in enemy_pokemon:
        for member in own_pokemon:

            # TODO: Simulation can be skipped in many cases, e.g. clear type advantage

            print(f"Getting matchup: {member.species} vs. {enemy.species}")

            enemy_possible_moves = enemy_builds[enemy.species].assumed_moves
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

                    test_own_build = PokemonBuild(member.species[0].upper() + member.species[1:], member.level)
                    ass = test_own_build.get_assumed_stat("spd")
                    print("Assumed: {}\nActual: {}".format(ass, member.stats["spd"]))

                    # print(enemy_builds[enemy.species].get_assumed_stat("spe") + enemy.base_stats["spe"])
                    # TODO: Does this take boosting into account?
                    enemy_is_faster = member.stats["spd"] < \
                                      enemy_builds[enemy.species].get_assumed_stat("spd") + enemy.base_stats["spd"]

                    print("Enemy is faster: {}".format(enemy_is_faster))

                    sys.exit(0)

    pass


if __name__ == "__main__":
    load_matchups_from_replays()
