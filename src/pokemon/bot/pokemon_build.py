"""Stores all Information gathered about a Pokemon"""
import json
from math import sqrt
from typing import List, Dict, Optional, Tuple

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon


# TODO: This only works for GEN1
class PokemonBuild:

    def __init__(self, species, level):

        self.base_stats = {}

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

        # EVs of the pokemon
        # TODO
        self.confirmed_evs: Optional[Dict[str, int]] = None

        # All possible IV combinations
        # Tuple: (evs, chance)
        # TODO
        self.possible_evs: List[Tuple[Dict[str, int], int]] = []

        # IVs of the pokemon
        # TODO
        self.confirmed_ivs: Optional[Dict[str, int]] = {}

        # All possible IV combinations#
        # Tuple: (ivs, chance)
        # TODO
        self.possible_ivs: List[Tuple[Dict[str, int], int]] = []

        # Stores all possible builds
        # Tuple: (build, int)
        # TODO: Remove builds no longer possible
        self.possible_builds: Tuple[dict, int] = []

        # TODO: Store all actions by this pokemon

        # Loading all possible builds
        file_content = open(f"src/pokemon/replays/data/{species.replace(' ', '')}.txt", "r").readlines()
        self.possible_builds = [tuple(line.split(" - ")[::-1]) for line in file_content if line.strip()]
        self.possible_builds = [(json.loads(t[0]), int(t[1])) for t in self.possible_builds]

        self.species = species
        self.level = level

        # Updating possible moves for the pokemon
        for possible_build in self.possible_builds:
            for move in possible_build[0]["moves"]:
                self.possible_moves[move] = self.possible_moves.get(move, 0) + possible_build[1]

        # print(f"Possible moves for {self.species}: {self.possible_moves}")

        self.reference_pokemon = Pokemon(species=self.species)

        self._update_ev_iv()

    def update_pokemon(self, pokemon: Pokemon):
        # print(f"Updating: {self.species}")
        # print(f"\tKnown moves: {pokemon.moves}")

        self.confirmed_moves = [move for move in self.possible_moves if move in pokemon.moves.keys()]

        # print(f"Confirmed moves: {self.confirmed_moves}")

        # TODO: Update possible moves based on build

        self._update_moves()

        self._update_ev_iv()

    def _update_moves(self, is_gen_one=True):
        # print("Possible moves before new evaluation:\n\t{}".format("\n\t".join(self.possible_moves)))

        # Removing confirmed moves from the dict containing all possible moves
        self.possible_moves = {k: v for k, v in self.possible_moves.items() if k not in self.confirmed_moves}

        self.assumed_moves = self.confirmed_moves + \
            sorted(self.possible_moves.keys(), key=lambda m: self.possible_moves[m])[:4 - len(self.confirmed_moves)]

        # print("Assumed moves:\n\t{}".format("\n\t".join(self.assumed_moves)))

    def get_assumed_stat(self, stat: str) -> int:
        """Formula: https://bulbapedia.bulbagarden.net/wiki/Stat"""

        # TODO: Calculate effective stats
        assert stat != "hp"

        if stat != "hp":
            base = self.reference_pokemon.base_stats[stat]
            dv = self.confirmed_ivs[stat]
            ev = self.confirmed_evs[stat]
            level = self.level

            return int(((((base + dv) * 2) + int(50 / 4)) * level) / 100) + 5




    def _update_ev_iv(self, is_gen_one=True):

        # TODO: This only works for gen1 so far
        assert is_gen_one

        # The only possible difference of two gen 1 pokemon is their move set
        if is_gen_one:
            self.confirmed_evs = self.possible_builds[0][0]["evs"]
            self.confirmed_ivs = self.possible_builds[0][0]["ivs"]


if __name__ == "__main__":
    b1 = PokemonBuild("Abra", 88)
