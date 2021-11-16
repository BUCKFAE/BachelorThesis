import os
import re
import json
import sys
import time

import matplotlib.pyplot as plt

from collections import Counter
from progress.bar import IncrementalBar
import itertools

REPLAY_PATH = "../anonymized-randbats"

REPLAY_LOAD_COUNT = 2_000


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
                if total == REPLAY_LOAD_COUNT: break


def main():
    pokemon_usage_count, player_ratings = extract_stats_from_replays(load_replays())

    plot_pokemon_usage(pokemon_usage_count)
    plot_player_ratings(player_ratings)


def extract_stats_from_replays(data, plot_count=5):
    # Storing how often what pokemon was used
    pokemon_usage_count = {}

    # Storing rating of all players
    player_ratings = []

    # Stores all builds of all pokemon
    pokemon_builds = {}

    bar = IncrementalBar('Loading Files:', max=REPLAY_LOAD_COUNT)

    for batch in data:

        for replay in batch:

            # Getting team information
            for team in [replay["p1team"], replay["p2team"]]:
                for pokemon in team:
                    name = pokemon["species"]
                    pokemon_usage_count[name] = pokemon_usage_count.get(name, 0) + 1

                    # Store all unique move sets for a pokemon as well as their appearance count
                    # TODO
                    evs = pokemon["evs"]
                    # print(evs)
                    # print(type(evs))

                    if name not in pokemon_builds:
                        pokemon_builds[name] = {}

                    for key, value in evs.items():
                        dict_key = f"{key}: {value}"
                        pokemon_builds[name][dict_key] = pokemon_builds[name].get(dict_key, 0) + 1

                    # print(pokemon_builds)

            # Getting player information
            input_log = replay["inputLog"]
            p1 = input_log[2]
            p2 = input_log[3]

            # Fixing replay with version-origin
            if not p1.startswith('>player p1'):
                l = [l for l in input_log if l.startswith('>player p1')]
                assert len(l) == 1
                p1 = l[0]
            if not p2.startswith('>player p2'):
                l = [l for l in input_log if l.startswith('>player p2')]
                assert len(l) == 1
                p2 = l[0]

            player_regex = re.compile(
                '>player p(1|2) {\\"\\"name\\":\\"[1-9][0-9]*\\",\\"rating\\":([0-9]*),\\"seed\\":\[[0-9]*,[0-9]*,[0-9]*,[0-9]*\]}')

            assert player_regex.match(p1)
            assert player_regex.match(p2)

            p1_rating = int(player_regex.search(p1).group(2))
            p2_rating = int(player_regex.search(p2).group(2))

            player_ratings.append((p1_rating, p2_rating))

            bar.next()

    bar.finish()

    for key, value in pokemon_builds.items():
        if len(value.values()) != 6:
            print(f"{key}: {pokemon_builds[key]}")


    return pokemon_usage_count, player_ratings


def plot_pokemon_usage(pokemon_usage_count, plot_count=5):
    pokemon_usage = [(k, pokemon_usage_count[k]) for k in pokemon_usage_count.keys()]
    pokemon_usage.sort(key=lambda t: t[1], reverse=True)

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
