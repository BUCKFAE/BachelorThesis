"""Stores all Information gathered about a Pokemon"""
import json
from typing import List, Dict, Optional, Tuple

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
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

        # TODO: This breaks for Mr. Mine

        # Loading all possible builds
        file_content = open(f"src/pokemon/replays/data/{species}.txt", "r").readlines()
        self.possible_builds = [tuple(line.split(" - ")[::-1]) for line in file_content if line.strip()]
        self.possible_builds = [(json.loads(t[0]), int(t[1])) for t in self.possible_builds]

        # print("Possible Builds for {}:\n\t{}".format(species, "\n\t".join([f"{t[0]} {t[1]}" for t in self.possible_builds])))

        self.species = species
        self.level = level

        # Updating possible moves for the pokemon
        for possible_build in self.possible_builds:
            for move in possible_build[0]["moves"]:
                self.possible_moves[move] = self.possible_moves.get(move, 0) + possible_build[1]

        # print(f"Possible moves for {self.species}: {self.possible_moves}")

    def update_pokemon(self, pokemon: Pokemon):
        # print(f"Updating: {self.species}")
        # print(f"\tKnown moves: {pokemon.moves}")

        self.confirmed_moves = [move for move in self.possible_moves if move in pokemon.moves.keys()]

        # print(f"Confirmed moves: {self.confirmed_moves}")

        # TODO: Update possible moves based on build



if __name__ == "__main__":
    b1 = PokemonBuild("Abra", 88)
