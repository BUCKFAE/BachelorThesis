import json
from typing import Dict, Any

from poke_env.environment.pokemon import Gen8Pokemon, Pokemon
from poke_env.environment.pokemon_gender import PokemonGender

from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.config import GENERATED_DATA_PATH
from src.pokemon.data_handling.util.species_names import convert_species_to_file_name


def load_pokemon_from_file(species) -> Gen8Pokemon:
    species_name = convert_species_to_file_name(species)

    # Loading the most likely build for the given species
    with open(f"{GENERATED_DATA_PATH}/{species_name}.txt") as f:
        build_dict = json.loads(f.readlines()[0].split(" - ")[1])

    # Creating the Pokémon
    build = build_from_string(species_name, build_dict)
    return pokemon_from_build(build)


def load_build_from_file(species) -> PokemonBuild:
    species_name = convert_species_to_file_name(species)

    # Loading the most likely build for the given species
    with open(f"{GENERATED_DATA_PATH}/{species_name}.txt") as f:
        build_dict = json.loads(f.readlines()[0].split(" - ")[1])

    # Creating the Pokémon
    return build_from_string(species_name, build_dict)


def build_from_string(species: str, build: Dict[str, Any]) -> PokemonBuild:
    pokemon_build = PokemonBuild(species,
                                 build["level"],
                                 build["gender"].upper(),
                                 build["item"],
                                 build["ability"])
    pokemon_build._possible_builds = [(
        {"ability": build["ability"],
         "stats": build["stats"],
         "gender": build["gender"].upper(),
         "item": build["item"],
         "level": build["level"],
         "moves": build["moves"]}, 1)]
    return pokemon_build


def pokemon_from_build(build: PokemonBuild) -> Pokemon:
    pokemon = Gen8Pokemon(species=build.species)
    pokemon._level = build.level
    pokemon.ability = build.get_most_likely_ability()
    pokemon._gender = PokemonGender.MALE if build.gender == "male" \
        else (PokemonGender.FEMALE if build.gender == "female" else PokemonGender.NEUTRAL)
    pokemon.item = build.get_most_likely_item()
    pokemon._last_request["stats"] = build.get_most_likely_stats()
    pokemon._moves = build.get_most_likely_moves()
    return pokemon
