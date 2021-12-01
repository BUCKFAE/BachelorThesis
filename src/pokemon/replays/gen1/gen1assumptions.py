"""Used to verify assumptions made about gen 1 random battles

Assumptions tested:
- No Pokemon has an ability [TRUE]
- The pokemon of the same species only differ in their moveset
"""
import json
import os
import sys

DATA_PATH = "src/pokemon/replays/data"


def _load_gen_1_data():
    for path, _, files in os.walk(DATA_PATH):
        for name in files:
            file_path = os.path.join(path, name)
            assert file_path.endswith(".txt")
            with open(file_path) as pokemon_data:
                yield pokemon_data.readlines()


def main():
    for pokemon_data in _load_gen_1_data():
        builds = [line.split(" - ")[1] for line in pokemon_data if line.strip()]
        builds = [json.loads(build) for build in builds]

        for build in builds:

            assert build["ability"] == "None"
            assert build["evs"] == builds[0]["evs"]
            assert build["ivs"] == builds[0]["ivs"]
            assert build["level"] == builds[0]["level"]
            assert build["item"] == ""



if __name__ == "__main__":
    main()
