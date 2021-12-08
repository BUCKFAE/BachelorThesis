"""Showdown sometimes changes the pool of pokemon"""
import sys
import os
import requests
import json
import ast
import re


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

    # print(data[:200])
    # print(data[-200:])

    data = json.loads(data)

    known_pokemon = []
    unknown_allowed = []

    for path, _, files in os.walk("src/pokemon/data_handling/data"):
        for name in files:
            known_pokemon.append(name.lower().rstrip(".txt"))

    print(f"Known Pokemon: {known_pokemon}")

    for key, value in data.items():
        if "isNonstandard" in value.keys():
            continue

        print(f"{key} -> {value}")

        if "tier" not in value.keys():
            print("Unknown tier!")
            continue

        if value["tier"] == "Illegal":
            continue


        if key not in known_pokemon:
            print("Unknown!")
            unknown_allowed.append(key)

    print(f"Unknown Pokemon:")
    print("\n\t".join(unknown_allowed))

    if "dialga" in unknown_allowed:
        print("ooh")

    print(len(unknown_allowed))

    print(type(data))


if __name__ == "__main__":
    main()
