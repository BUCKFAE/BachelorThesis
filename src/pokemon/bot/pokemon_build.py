"""Stores all Information gathered about a Pokemon"""
import json
from typing import List, Dict, Optional, Tuple

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.pokemon import Pokemon


class PokemonBuild:

    base_stats = {}

    # List of moves the pokemon used previously
    confirmed_moves: List[str] = []

    # List of moves the pokemon may know
    # Key: name of the move
    # Value: Chance that the pokemon knows this move
    possible_moves: Dict[str, int] = {}

    # Item we know the pokemon has
    confirmed_item: Optional[str] = None

    # List of items the pokemon may hold
    # Key: name of the item
    # Value: Chance that the pokemon holds this item
    possible_items: Dict[str, int] = {}

    # EVs of the pokemon
    confirmed_evs: Optional[Dict[str, int]] = None

    # All possible IV combinations
    # Tuple: (evs, chance)
    possible_evs: List[Tuple[Dict[str, int], int]] = []

    # IVs of the pokemon
    confirmed_ivs: Optional[Dict[str, int]] = {}

    # All possible IV combinations#
    # Tuple: (ivs, chance)
    possible_ivs: List[Tuple[Dict[str, int], int]] = []

    # Stores all possible builds
    # Tuple: (build, int)
    possible_builds: Tuple[dict, int] = []

    # TODO: Store all actions by this pokemon

    def __init__(self, species, level):

        # Loading all possible builds
        file_content = open(f"src/pokemon/replays/data/{species}.txt", "r").readlines()
        self.possible_builds = [tuple(line.split(" - ")[::-1]) for line in file_content if line.strip()]
        self.possible_builds = [(json.loads(t[0]), t[1]) for t in self.possible_builds]

        print(f"Possible Builds for {species}:")
        print("\n\t".join([f"{t[0]} {t[1]}" for t in self.possible_builds]))

        self.species = species
        self.level = level

    def update_pokemon(self, pokemon: Pokemon):
        print("Updating")

if __name__ == "__main__":
    b1 = PokemonBuild("Flapple", 82)
