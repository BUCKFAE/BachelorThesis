"""Used to generate all possible gen 1 builds
# TODO
"""
import asyncio
import json
import os
import shutil

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.pokemon_gender import PokemonGender
from poke_env.player.battle_order import BattleOrder, ForfeitBattleOrder
from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from progress.bar import IncrementalBar

from src.pokemon.replays.util import convert_species_to_file_name

PATH = "src/pokemon/replays/generated-data"
NUM_BATTLES = 500


class DumpingPlayer(Player):

    def __init__(self, battle_format, num_battles):
        super().__init__(battle_format=battle_format, max_concurrent_battles=1)

        # {Pikachu: {<build1>: 20, <build2>: 30}}
        self.builds = {}

        # Progress bar
        self.bar = IncrementalBar('Generating Games:', max=num_battles)

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        if battle.turn == 1:

            for pokemon in battle.team:


                # Extract data from replay
                name = convert_species_to_file_name(battle.team[pokemon].species)

                if "porygon" in name:
                    print(name)

                ability = battle.team[pokemon].ability
                stats = battle.team[pokemon].stats
                gender = battle.team[pokemon].gender
                item = battle.team[pokemon].item
                level = battle.team[pokemon].level
                moves = battle.team[pokemon].moves

                # Creating dict that represents the build
                build = {"ability": ability,
                         "stats": stats,
                         "gender": "male" if gender == PokemonGender.MALE else ("female" if PokemonGender.FEMALE
                                                                                else "neutral"),
                         "item": item,
                         "level": level,
                         "moves": "[{}]".format("|".join(sorted(moves)))}

                # Saving the build
                build_string = json.dumps(build)

                # Inserting name if not yet present
                if name not in self.builds:
                    self.builds[name] = {}

                # Counting how many times the build appeared
                self.builds[name][build_string] = self.builds[name].get(build_string, 0) + 1

            self.bar.next()

        if battle.turn == 3:
            return ForfeitBattleOrder()

        return self.choose_random_move(battle)

    def write_builds_to_files(self):
        print("Writing Pokemon builds to file!")

        # Clearing data directory
        if os.path.exists("src/pokemon/replays/data/generated"):
            shutil.rmtree("src/pokemon/replays/data/generated")
        os.mkdir("src/pokemon/replays/data/generated")

        # Writing all builds to file
        for pokemon in self.builds:
            with open(f"src/pokemon/replays/data/generated/{pokemon}.txt", "w") as pokemon_file:
                for build, usage_count in sorted(self.builds[pokemon].items(), key=lambda x: x[1], reverse=True):
                    pokemon_file.write(f"{usage_count} - {build}\n\n")

        print("Finished writing builds to file!")


async def main():
    # Deleting old data dir
    shutil.rmtree(PATH)
    os.mkdir(PATH)

    p1 = DumpingPlayer(battle_format="gen8randombattle", num_battles=NUM_BATTLES)
    p2 = RandomPlayer(battle_format="gen8randombattle")

    await p1.battle_against(p2, n_battles=NUM_BATTLES)
    p1.bar.finish()

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Random")

    # print(p1.builds["charizard"])
    p1.write_builds_to_files()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
