"""Used to verify that pokemon are actually missing"""
import os
import json
import sys

from progress.bar import IncrementalBar

REPLAY_PATH = "../anonymized-randbats"
REPLAY_LOAD_COUNT = 8521536


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


def extract_data():

    bar = IncrementalBar('Loading Files:', max=REPLAY_LOAD_COUNT)

    for batch in load_replays():
        for replay in batch:
            for team in [replay["p1team"], replay["p2team"]]:
                for pokemon in team:
                    name = pokemon["species"]

                    if "Dialga" in name:
                        print("Found Dialga!")
                        bar.finish()
                        sys.exit(0)

            bar.next()
    bar.finish()


if __name__ == "__main__":
    extract_data()
