import json
import os

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.damage_calculator import extract_evs_ivs_from_build, get_total_stat
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.config import GENERATED_DATA_PATH


def remove_illegal_pokemon_builds():
    """
    Removes illegal builds
    """

    for path, _, files in os.walk(GENERATED_DATA_PATH):
        for file_name in files:

            legal_builds = []

            with open(f"{GENERATED_DATA_PATH}/{file_name}", "r") as pokemon_file:
                for build_string in [b.strip() for b in pokemon_file.readlines() if b.strip()]:
                    build = json.loads(build_string.split(" - ")[1])

                    pokemon_build = PokemonBuild(file_name.replace(".txt", ""),
                                                 build["level"],
                                                 build["gender"].upper(),
                                                 build["item"],
                                                 build["ability"])

                    # Removing all invalid builds
                    pokemon_build._possible_builds = [b for b in pokemon_build._possible_builds
                                                      if b[0]["stats"] == build["stats"]]

                    # Getting assumed evs and ivs for the Pokémon
                    evs, ivs = extract_evs_ivs_from_build(pokemon_build)

                    is_valid = True
                    # Ensuring the assumed stats match the actual stat
                    for stat in build["stats"]:
                        calculated_stat = get_total_stat(pokemon_build.base_stats, evs, ivs, build["level"], stat)
                        if calculated_stat != build["stats"][stat]:
                            is_valid = False
                            logger.warning(f"Invalid build for Pokémon!\n"
                                           f"\tSpecies: {file_name.replace('.txt', '')}\n"
                                           f"\tBuild: {build}")

                    if is_valid:
                        legal_builds.append(build_string)

            with open(f"{GENERATED_DATA_PATH}/{file_name}", "w") as pokemon_file:
                for legal_build in legal_builds:
                    pokemon_file.write(f"{legal_build}\n\n")


if __name__ == "__main__":
    remove_illegal_pokemon_builds()
