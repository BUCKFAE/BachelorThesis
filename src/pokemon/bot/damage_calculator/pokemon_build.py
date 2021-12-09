"""Stores all Information gathered about a Pokémon"""
import json
from typing import List, Dict, Optional, Tuple, Set

from poke_env.environment.pokemon import Pokemon

# TODO: This only works for GEN1
from src.pokemon.config import GENERATED_DATA_PATH
from src.pokemon.data_handling.util import convert_species_to_file_name


class PokemonBuild:

    def __init__(self,
                 species: str,
                 level: int,
                 gender: str,
                 item: str,
                 ability: Optional[str]):
        """
        If we don't know the item yet, poke-env returns `unknown_item`
        """

        # Species of the Pokémon
        self.species = convert_species_to_file_name(species)

        # print(f"Creating build for species: {self.species}")

        # Loading all possible builds
        with open(f"{GENERATED_DATA_PATH}/{self.species}.txt", "r") as f:
            file_content = f.readlines()
        self._possible_builds = [tuple(line.split(" - ")[::-1]) for line in file_content if line.strip()]
        self._possible_builds = [(json.loads(t[0]), int(t[1])) for t in self._possible_builds]

        # Level of the Pokémon
        self.level = level
        # print(f"\tLevel: {level}")
        self._remove_invalid_builds_level()

        # Gender of the Pokémon
        if not (gender == "MALE" or gender == "FEMALE" or gender == "NEUTRAL"):
            raise ValueError("Invalid gender! Expected \"MALE\", \"FEMALE\" or \"NEUTRAL\"")
        self.gender = gender.lower()
        # print(f"\tGender: {self.gender}")
        self._remove_invalid_builds_gender()

        # Getting all possible abilities
        self._confirmed_ability = ability
        self._possible_abilities: List[str] = list(set([build[0]["ability"] for build in self._possible_builds]))

        # The Pokémon always has the same ability
        if len(self._possible_abilities) == 1:
            self._confirmed_ability = self._possible_abilities[0]

        # Ensuring we know this build
        if self._confirmed_ability is not None and self._confirmed_ability not in self._possible_abilities:
            raise ValueError(f"Received an unknown ability for Pokémon \"{species}\"\n"
                             f"\tKnown: {list(self._possible_abilities)}\n"
                             f"\tReceived: {ability}")
        # print(f"\tAbility: {ability}")
        self._remove_invalid_builds_ability()

        # Item we know the Pokémon has
        self._confirmed_item: Optional[str] = None if item == "unknown_item" else item

        # List of items the Pokémon may hold
        # Key: name of the item
        # Value: How often the Pokémon was holding this item
        self._possible_items: List[str] = list(set([build[0]["item"] for build in self._possible_builds]))
        self._remove_invalid_builds_item()

        # List of moves the Pokémon used previously
        self._confirmed_moves: List[str] = []

        # List of moves the Pokémon may know
        # Key: name of the move
        # Value: How often the Pokémon knew this move
        self._possible_moves: Dict[str, int] = {}

        # Updating possible moves for the Pokémon
        for possible_build in self._possible_builds:
            for move in possible_build[0]["moves"].split("|"):
                self._possible_moves[move] = self._possible_moves.get(move, 0) + possible_build[1]

        # Confirmed total stats of the Pokémon
        self._confirmed_stats: Dict[str, int] = {}

        # Possible total stats of the Pokémon
        self._possible_stats: List[Dict[str, int], int] = \
            list(set([json.dumps(build[0]["stats"], sort_keys=True) for build in self._possible_builds]))
        self._possible_stats = [json.loads(build) for build in self._possible_stats]

        # Getting base stats for the Pokémon
        self.reference_pokemon = Pokemon(species=self.species)
        self.base_stats = self.reference_pokemon.base_stats

        # Removing invalid builds
        self._remove_invalid_builds()

    def update_pokemon(self, pokemon: Pokemon):

        print(f"Updating info of {pokemon.species}")

    def _remove_invalid_builds(self):
        self._remove_invalid_builds_level()
        self._remove_invalid_builds_gender()
        self._remove_invalid_builds_ability()
        self._remove_invalid_builds_item()

    def _remove_invalid_builds_level(self):
        self._possible_builds = [b for b in self._possible_builds if b[0]["level"] == self.level]

    def _remove_invalid_builds_gender(self):
        self._possible_builds = [b for b in self._possible_builds if b[0]["gender"] == self.gender]

    def _remove_invalid_builds_ability(self):
        self._possible_builds = [b for b in self._possible_builds
                                 if b[0]["ability"] == self._confirmed_ability or
                                 self._confirmed_ability is None]

    def _remove_invalid_builds_item(self):
        if self._confirmed_item is not None:
            self._possible_builds = [b for b in self._possible_builds if b[0]["item"] == self._confirmed_item]

    def get_most_likely_moves(self):
        """Returns the most likely moves of the given Pokémon
        The most likely moves are the moves of the most likely build"""
        return self.get_most_likely_build()["moves"].split("|")

    def get_most_likely_item(self):
        """Returns the most likely item of the given Pokémon"""
        return self.get_most_likely_build()["item"]

    def get_most_likely_ability(self):
        return self.get_most_likely_build()["ability"]

    def get_most_likely_stats(self):
        """Returns the most likely stats of the given Pokémon"""
        return self.get_most_likely_build()["stats"]

    def get_most_likely_build(self):
        """Returns the most likely build"""
        return max(self._possible_builds, key=lambda x: x[1])[0]


if __name__ == "__main__":
    b1 = PokemonBuild("Charizard", 82, "MALE", "unknown_item", None)
    print(f"Most likely build: {b1.get_most_likely_build()}")
    print(f"Most likely moves: {b1.get_most_likely_moves()}")
    print(f"Most likely item: {b1.get_most_likely_item()}")