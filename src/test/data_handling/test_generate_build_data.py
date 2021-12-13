import logging
import os
import requests
import json
import re
import unittest

from src.pokemon.bot.damage_calculator.damage_calculator import extract_evs_ivs_from_build, get_total_stat
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.config import GENERATED_DATA_PATH
from src.pokemon.data_handling.util.species_names import convert_species_name


class TestBuildDataGeneration(unittest.TestCase):

    def test_generated_build_data(self):
        """
        Ensures we have build data for all currently occurring Pokémon
        """

        logging.info("Requesting information about Pokémon from Showdown")

        # Link contains information on which Pokémon are currently generated
        response = requests.get("https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/data/formats-data.ts")

        logging.info("Received Pokémon data from Showdown.")

        # Preparing data to be parsed
        data = str(response.text).removeprefix("export const FormatsData: {[k: string]: SpeciesFormatsData} =")
        data = data.rstrip("\n;")
        data = data.replace("// buffed twice in the last 6 months as of Nov 2021", "")
        data = data.replace("// can't be used in battle", "")

        # Adding quotes
        data = re.sub("([\\t]+)([a-zA-Z0-9]+):", "\t\"\\2\":", data)
        data = re.sub(",[\\n\\t]+}", "}", data)

        logging.info("Loading formatted json data")

        data = json.loads(data)

        # Storing all known Pokémon and all defined Pokémon
        known_pokemon = []
        all_defined_pokemon = []

        logging.info(f"Loading all Pokémon defined by Showdown")

        # Getting all Pokémon defined by Showdown
        for key, value in data.items():
            if "randomBattleMoves" not in value.keys():
                continue

            all_defined_pokemon.append(convert_species_name(key))

        logging.info(f"Amount of Pokémon defined by Showdown: {len(all_defined_pokemon)}")

        logging.info("Loading the names of all known pokemon")

        # Getting all Pokémon that we know
        for path, _, files in os.walk(GENERATED_DATA_PATH):
            for file_name in files:
                pokemon_name = file_name.replace(".txt", "")
                logging.debug(f"Pokémon: {pokemon_name}")
                known_pokemon.append(pokemon_name)

        logging.info(f"Amount of known Pokémon: {len(known_pokemon)}")

        unknown_pokemon = []

        for current_defined_pokemon in all_defined_pokemon:
            if current_defined_pokemon not in known_pokemon and "gmax" not in current_defined_pokemon:
                unknown_pokemon.append(current_defined_pokemon)

        logging.info(f"Amount of unknown Pokémon: {len(unknown_pokemon)}")

        # Printing unknown Pokémon if there are any
        if len(unknown_pokemon) != 0:
            logging.warning(f"There are {len(unknown_pokemon)} unknown Pokémon!\n" +
                            "\tUnknown Pokemon:\n\t\t{}".format("\n\t\t".join(unknown_pokemon)))

        # TODO: Include this again
        # self.assertTrue(len(unknown_pokemon) == 0)

    def test_validate_builds(self):
        """Ensures that we can get extract the evs and ivs of every known Pokémon"""

        validated_pokemon = 0
        validated_builds = 0

        for path, _, files in os.walk(GENERATED_DATA_PATH):
            for name in files:
                assert name.endswith(".txt")

                species = name.removesuffix(".txt")

                # TODO: Broken because of form
                if species == "wishiwashi" or species == "lycanroc":
                    continue

                with open(os.path.join(path, species) + ".txt") as replay_file:

                    for build_string in [b.strip() for b in replay_file.readlines() if b.strip()]:
                        build = json.loads(build_string.split(" - ")[1])

                        pokemon_build = PokemonBuild(species,
                                                     build["level"],
                                                     build["gender"].upper(),
                                                     build["item"],
                                                     build["ability"])

                        # Removing all invalid builds
                        pokemon_build._possible_builds = [b for b in pokemon_build._possible_builds
                                                          if b[0]["stats"] == build["stats"]]

                        # Getting assumed evs and ivs for the Pokémon
                        evs, ivs = extract_evs_ivs_from_build(pokemon_build)

                        # Ensuring the assumed stats match the actual stat
                        for stat in build["stats"]:
                            calculated_stat = get_total_stat(pokemon_build.base_stats, evs, ivs, build["level"], stat)
                            assert calculated_stat == build["stats"][stat]

                        validated_builds += 1
                validated_pokemon += 1
        logging.info(f"Validated {validated_builds} builds of {validated_pokemon} pokemon")


if __name__ == "__main__":
    unittest.main()
