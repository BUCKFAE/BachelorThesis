import json
import sys

from src.pokemon.replays.load_replays import load_replays

if __name__ == "__main__":
    target = input("Property: ")

    # Looking through replays until property is found
    for batch in load_replays():
        for replay in batch:
            for team in [replay["p1team"], replay["p2team"]]:
                for pokemon in team:
                    moves = pokemon["moves"]

                    # Move matches
                    if target in moves or target in pokemon["ability"] or target in pokemon["item"]:
                        print(json.dumps(pokemon, indent=4, sort_keys=True))
                        sys.exit(0)
