import os
import re
import json

import matplotlib.pyplot as plt

from collections import Counter
from progress.bar import IncrementalBar
import itertools

# TODO: Improve path import
REPLAY_PATH = "data/"

REPLAY_LOAD_COUNT = 20_000


def main():
    data = []

    replays_loaded = 0

    bar = IncrementalBar('Loading Files:', max=REPLAY_LOAD_COUNT)

    # TODO: Make this an iterator so this doesn't have to be loaded to ram
    for path, _, files in os.walk(REPLAY_PATH):
        for name in files:
            file_path = os.path.join(path, name)
            assert file_path.endswith(".log.json")

            with open(file_path) as replay_file:
                data.append(json.load(replay_file))
        
            bar.next()

            replays_loaded += 1
            if replays_loaded == REPLAY_LOAD_COUNT: break

    bar.finish()

    get_pokemon_usage(data)

def get_pokemon_usage(data, plot_count=5):

    pokemon_usage_count = {}

    for team in itertools.chain(*[[d["p1team"], d["p2team"]] for d in data]):
        for pokemon in team:
            name = pokemon["species"]
            pokemon_usage_count[name] = pokemon_usage_count.get(name, 0) + 1

    pokemon_usage = [(k, pokemon_usage_count[k]) for k in pokemon_usage_count.keys()]
    pokemon_usage.sort(key=lambda t: t[1], reverse=True)

    average_usage = sum([u[1] for u in pokemon_usage]) / len(pokemon_usage)

    plt.bar(*zip(*pokemon_usage[:plot_count]))
    plt.title(f"Top {plot_count} used pokemon:\nAverage: {int(average_usage)}")
    plt.show()

def get_player_ratings(data):
    # Getting the rating of all players
    player_ratings = []
    for input_log in [d["inputLog"] for d in data]:
        p1 = input_log[2]
        p2 = input_log[3]

        player_regex = re.compile('>player p(1|2) {\\"\\"name\\":\\"[1-9][0-9]*\\",\\"rating\\":([0-9]*),\\"seed\\":\[[0-9]*,[0-9]*,[0-9]*,[0-9]*\]}')

        assert player_regex.match(p1)
        assert player_regex.match(p2)

        p1_rating = int(player_regex.search(p1).group(2))
        p2_rating = int(player_regex.search(p2).group(2))

        player_ratings.append((p1_rating, p2_rating))

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
