import json
import os
import sys
from typing import List

from src.pokemon.config import GENERATED_DATA_PATH


def find_pokemon_knows_move(move: str) -> List[str]:
    """Returns a list of all Pokemon names that know this move in their most likely build"""
    pokemon_knowing_move = []
    for path, _, files in os.walk(GENERATED_DATA_PATH):
        for name in files:
            current_file = os.path.join(path, name)
            with open(current_file, 'r') as pokemon_file:
                first_build = pokemon_file.readlines()[0].split(" - ")[1]
                build = json.loads(first_build)
                moves = build["moves"].split("|")
                if move in moves:
                    pokemon_knowing_move.append(name.strip(".txt"))

    return pokemon_knowing_move


if __name__ == "__main__":
    args = sys.argv
    assert len(args) == 2
    print(find_pokemon_knows_move(args[1]))

