import os
import re
import json
import glob
import sys
from typing import Tuple

import matplotlib.pyplot as plt

from collections import Counter
from progress.bar import IncrementalBar

from src.pokemon.replays.replay_data import ReplayData

REPLAY_PATH = "../gen1anon"

# Total: 8521536
REPLAY_LOAD_COUNT = 98670


def load_replays(batch_size=64):
    batch = []
    total = 0

    for path, _, files in os.walk(REPLAY_PATH):
        for name in files:
            file_path = os.path.join(path, name)
            assert file_path.endswith(".log.json")

            with open(file_path) as replay_file:
                batch.append(json.load(replay_file))

            total += 1

            if len(batch) == batch_size or total == REPLAY_LOAD_COUNT:
                yield batch
                batch.clear()
                if total == REPLAY_LOAD_COUNT:
                    break


def main():
    replay_data = extract_stats_from_replays(load_replays())

    plot_pokemon_usage(replay_data.pokemon_builds)
    plot_player_ratings(replay_data.player_ratings)

    safe_builds_to_files(replay_data.pokemon_builds)

    plot_hazard_sets(replay_data)


def extract_stats_from_replays(d):
    data = ReplayData()

    bar = IncrementalBar('Loading Files:', max=REPLAY_LOAD_COUNT)

    for batch in d:

        for replay in batch:

            # ID of the current team
            tid = -1

            # For both teams: # Pokemon that can set / clear hazards
            hazard_control = [[[False] * 6, [False] * 6], [[False] * 6, [False] * 6]]

            # Storing the builds for all pokemon
            for team in [replay["p1team"], replay["p2team"]]:

                tid += 1
                pid = -1

                # Extracting builds from team
                for pokemon in team:

                    pid += 1

                    name = pokemon["species"].replace(" ", "")

                    if "alga" in name:
                        print(name)

                    # Sorting moves as they often are in different orders
                    pokemon["moves"] = sorted(pokemon["moves"])

                    if name not in data.pokemon_builds:
                        data.pokemon_builds[name] = {}

                    build = json.dumps(pokemon)
                    data.pokemon_builds[name][build] = data.pokemon_builds[name].get(build, 0) + 1

                    # Todo: G-Max Steelsurge is not handled
                    hazards = ["spikes", "stealthrock", "stickyweb", "toxicspikes"]
                    anti_hazards = ["rapidspin", "defog"]

                    for hazard in hazards:
                        if hazard in pokemon["moves"]:
                            data.hazards[hazard] = data.hazards.get(hazard, 0) + 1
                            hazard_control[tid][0][pid] = True

                    for anti_hazard in anti_hazards:
                        if anti_hazard in pokemon["moves"]:
                            data.anti_hazards[anti_hazard] = data.anti_hazards.get(anti_hazard, 0) + 1
                            hazard_control[tid][1][pid] = True

                    if "Heavy-Duty Boots" in pokemon["item"]:
                        data.boots += 1
                        hazard_control[tid][1][pid] = True

            # Evaluating Hazards
            data.hazard_vs_clear += 1 if any(hazard_control[0][0]) and any(hazard_control[1][1]) else 0
            data.hazard_vs_clear += 1 if any(hazard_control[1][0]) and any(hazard_control[0][1]) else 0

            data.hazard_vs_no_clear += 1 if any(hazard_control[0][0]) and not any(hazard_control[1][1]) else 0
            data.hazard_vs_no_clear += 1 if any(hazard_control[1][0]) and not any(hazard_control[0][1]) else 0

            data.no_hazard_vs_clear += 1 if not any(hazard_control[0][0]) and any(hazard_control[1][1]) else 0
            data.no_hazard_vs_clear += 1 if not any(hazard_control[1][0]) and any(hazard_control[0][1]) else 0

            data.no_hazard_vs_no_clear += 1 if not any(hazard_control[0][0]) and not any(hazard_control[1][1]) else 0
            data.no_hazard_vs_no_clear += 1 if not any(hazard_control[1][0]) and not any(hazard_control[0][1]) else 0

            # Getting player information
            input_log = replay["inputLog"]
            try:
                p1 = input_log[2]
                p2 = input_log[3]
            except:
                continue
            # Fixing replay with version-origin
            if not p1.startswith('>player p1'):
                a = [a for a in input_log if a.startswith('>player p1')]
                assert len(a) == 1
                p1 = a[0]
            if not p2.startswith('>player p2'):
                a = [a for a in input_log if a.startswith('>player p2')]
                assert len(a) == 1
                p2 = a[0]

            player_regex = re.compile(
                '>player p([12]) {\\"\\"name\\":\\"[1-9][0-9]*\\",\\"rating\\":([0-9]*),\\"seed\\":\\[[0-9]*,[0-9]*,'
                '[0-9]*,[0-9]*]}')

            assert player_regex.match(p1)
            assert player_regex.match(p2)

            p1_rating = int(player_regex.search(p1).group(2))
            p2_rating = int(player_regex.search(p2).group(2))

            data.player_ratings.append((p1_rating, p2_rating))

            bar.next()

    bar.finish()

    return data


def safe_builds_to_files(builds):
    """Creates a file for each pokemon listing all it's possible builds"""

    # Assert that data dir exists
    assert os.path.exists("src/pokemon/replays/data")

    # Clearing old files in the data directory
    for f in glob.glob("src/pokemon/replays/data/*"):
        os.remove(f)

    for pokemon_name, pokemon_builds in builds.items():

        with open(f"src/pokemon/replays/data/{pokemon_name}.txt", "w") as pokemon_file:

            for pokemon_build, build_usage_count in pokemon_builds.items():
                pokemon_file.write(f"{build_usage_count} - ")
                pokemon_file.write(pokemon_build)
                pokemon_file.write("\n\n")


def plot_hazard_sets(replay_data):
    graph_label = ["Hazard\nvs\nClear",
                   "Hazard\nvs\nNo Clear",
                   "No Hazard\nvs\nClear",
                   "No Hazard\nvs\nno Clear"]
    graph_data = [replay_data.hazard_vs_clear,
                  replay_data.hazard_vs_no_clear,
                  replay_data.no_hazard_vs_clear,
                  replay_data.no_hazard_vs_no_clear]

    # Two players in each game
    assert sum(graph_data) == 2 * REPLAY_LOAD_COUNT

    plt.bar(graph_label, graph_data)
    plt.subplots_adjust(bottom=0.15)
    plt.title(f"Hazard / Control Distribution\nGames: {REPLAY_LOAD_COUNT}")
    plt.show()


def plot_pokemon_usage(builds, plot_count=5):
    # Stores how often what pokemon is used
    pokemon_usage = []

    for key, value in builds.items():
        curr = [key, 0]
        for build_count in value.values():
            curr[1] += build_count
        pokemon_usage += [curr]

    pokemon_usage.sort(key=lambda x: x[1], reverse=True)

    average_usage = sum([u[1] for u in pokemon_usage]) / len(pokemon_usage)

    plt.bar(*zip(*pokemon_usage[:plot_count]))
    plt.title(f"Top {plot_count} used pokemon:\nAverage: {int(average_usage)}")
    plt.show()


def plot_player_ratings(player_ratings):
    p1 = Counter([t[0] for t in player_ratings])
    p1_sum = [(k, p1[k]) for k in p1.keys()]
    p1_sum.sort(key=lambda t: t[0])

    p2 = Counter([t[1] for t in player_ratings])
    p2_sum = [(k, p2[k]) for k in p2.keys()]
    p2_sum.sort(key=lambda t: t[0])

    plt.plot(*zip(*p1_sum), label="Elo Player 1")
    plt.plot(*zip(*p2_sum), label="Elo Player 2")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
