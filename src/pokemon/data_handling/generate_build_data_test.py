"""Showdown sometimes changes the pool of Pokémon"""
import sys
import os
import requests
import json
import ast
import re

from src.pokemon.config import GENERATED_DATA_PATH


def main():
    response = requests.get("https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/data/formats-data.ts")

    # Preparing data to be parsed
    data = str(response.text).removeprefix("export const FormatsData: {[k: string]: SpeciesFormatsData} =")
    data = data.rstrip("\n;")
    data = data.replace("// buffed twice in the last 6 months as of Nov 2021", "")
    data = data.replace("// can't be used in battle", "")

    # Adding quotes
    data = re.sub("([\\t]+)([a-zA-Z0-9]+):", "\t\"\\2\":", data)
    data = re.sub(",[\\n\\t]+}", "}", data)

    data = json.loads(data)

    known_pokemon = []
    all_defined_pokemon = []

    for path, _, files in os.walk(GENERATED_DATA_PATH):
        for name in files:
            print(name)
            known_pokemon.append(name.replace(".txt", ""))

    print(f"Known Pokemon: {known_pokemon}")

    print(f"Amount of known pokemon: {len(known_pokemon)}")

    for key, value in data.items():
        if "randomBattleMoves" not in value.keys():
            continue
        all_defined_pokemon.append(key)

    print(f"Amount of defined pokemon: {len(all_defined_pokemon)}")

    unknown_pokemon = []

    for current_defined_pokemon in all_defined_pokemon:
        if current_defined_pokemon not in known_pokemon:
            unknown_pokemon.append(current_defined_pokemon)

    print(f"Unknown Pokemon: {unknown_pokemon}")


if __name__ == "__main__":
    main()
