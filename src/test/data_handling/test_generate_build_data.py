import logging
import os
import requests
import json
import re
import unittest

from src.pokemon.config import GENERATED_DATA_PATH
from src.pokemon.data_handling.util.species_names import convert_species_name


class TestBuildDataGeneration(unittest.TestCase):

    def test_generated_build_data(self):
        """
        Ensures we have build data for all currently occurring Pokémon
        """

        logging.info("Requesting information about all Pokémon from Showdown")

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

        logging.info("Loading unknown Pokémon")

        unknown_pokemon = []

        for current_defined_pokemon in all_defined_pokemon:
            if current_defined_pokemon not in known_pokemon:
                unknown_pokemon.append(current_defined_pokemon)

        logging.info(f"Amount of unknown Pokémon: {len(unknown_pokemon)}")

        # Printing unknown Pokémon if there are any
        if len(unknown_pokemon) != 0:
            logging.warning(f"There are {len(unknown_pokemon)} unknown Pokémon!\n" +
                            "\tUnknown Pokemon:\n\t\t{}".format("\n\t\t".join(unknown_pokemon)))

        self.assertTrue(len(unknown_pokemon) == 0)

if __name__ == "__main__":
    unittest.main()
