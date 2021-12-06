"""Stores all Information gathered about a Pokemon"""
import json
from math import sqrt
from typing import List, Dict, Optional, Tuple

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon


# TODO: This only works for GEN1
from src.pokemon.replays.util import convert_species_to_file_name


class PokemonBuild:

    def __init__(self, species, level):

        # List of moves the pokemon used previously
        self.confirmed_moves: List[str] = []

        # List of moves the pokemon may know
        # Key: name of the move
        # Value: Chance that the pokemon knows this move
        self.possible_moves: Dict[str, int] = {}

        # The moves we assume the pokemon to have based on the information we've gathered
        self.assumed_moves: List[str] = []

        # Item we know the pokemon has
        # TODO
        self.confirmed_item: Optional[str] = None

        # List of items the pokemon may hold
        # Key: name of the item
        # Value: Chance that the pokemon holds this item
        # TODO
        self.possible_items: Dict[str, int] = {}

        # Confirmed stats of the pokemon (including ev and iv)
        # TODO
        self.confirmed_stats: Optional[Dict[str, int]] = None

        # Possible stats of the pokemon (including ev and iv)
        # Tuple: (evs, chance)
        # TODO
        self.possible_stats: List[Tuple[Dict[str, int], int]] = []

        # Stores all possible builds
        # Tuple: (build, int)
        # TODO: Remove builds no longer possible
        self.possible_builds: Tuple[dict, int] = []

        # TODO: Store all actions by this pokemon

        self.species = convert_species_to_file_name(species)


        # Loading all possible builds
        file_content = open(f"src/pokemon/replays/data/generated/{self.species}.txt", "r").readlines()
        self.possible_builds = [tuple(line.split(" - ")[::-1]) for line in file_content if line.strip()]
        self.possible_builds = [(json.loads(t[0]), int(t[1])) for t in self.possible_builds]


        self.level = level

        # Updating possible moves for the pokemon
        for possible_build in self.possible_builds:
            for move in possible_build[0]["moves"]:
                self.possible_moves[move] = self.possible_moves.get(move, 0) + possible_build[1]

        # print(f"Possible moves for {self.species}: {self.possible_moves}")

        self.reference_pokemon = Pokemon(species=self.species)
        self.base_stats = self.reference_pokemon.base_stats

    def update_pokemon(self, pokemon: Pokemon):
        # print(f"Updating: {self.species}")
        # print(f"\tKnown moves: {pokemon.moves}")

        self.confirmed_moves = [move for move in self.possible_moves if move in pokemon.moves.keys()]

        # print(f"Confirmed moves: {self.confirmed_moves}")

        # TODO: Update possible moves based on build

        self._update_moves()


    def _update_moves(self):
        # print("Possible moves before new evaluation:\n\t{}".format("\n\t".join(self.possible_moves)))

        # Removing confirmed moves from the dict containing all possible moves
        self.possible_moves = {k: v for k, v in self.possible_moves.items() if k not in self.confirmed_moves}

        self.assumed_moves = self.confirmed_moves + \
            sorted(self.possible_moves.keys(), key=lambda m: self.possible_moves[m])[:4 - len(self.confirmed_moves)]

        # print("Assumed moves:\n\t{}".format("\n\t".join(self.assumed_moves)))


    def _update_stats(self):
        # TODO
        pass


if __name__ == "__main__":
    b1 = PokemonBuild("Abra", 88)
