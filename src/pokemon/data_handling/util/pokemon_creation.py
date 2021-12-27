"""Used to quickly create Pokémon and PokemonBuilds"""

import json
from typing import Dict, Any

from poke_env.environment.move import Move
from poke_env.environment.pokemon import Gen8Pokemon, Pokemon
from poke_env.environment.pokemon_gender import PokemonGender

from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.config import GENERATED_DATA_PATH
from src.pokemon.data_handling.util.species_names import convert_species_name


def load_pokemon_from_file(species) -> Gen8Pokemon:
    """
    Creates the most likely Pokémon with the corresponding name
    """
    species_name = convert_species_name(species)

    # Loading the most likely build for the given species
    with open(f"{GENERATED_DATA_PATH}/{species_name}.txt") as f:
        build_dict = json.loads(f.readlines()[0].split(" - ")[1])

    # Creating the Pokémon
    build = build_from_string(species_name, build_dict)
    return pokemon_from_build(build)


def load_build_from_file(species) -> PokemonBuild:
    """
    Creates the most likely PokemonBuild of a Pokémon with the corresponding name
    """
    species_name = convert_species_name(species)

    # Loading the most likely build for the given species
    with open(f"{GENERATED_DATA_PATH}/{species_name}.txt") as f:
        build_dict = json.loads(f.readlines()[0].split(" - ")[1])

    # Creating the Pokémon
    return build_from_string(species_name, build_dict)


def build_from_string(species: str, build: Dict[str, Any]) -> PokemonBuild:
    """Creates the PokemonBuild described by the given string"""
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


def build_from_pokemon(pokemon: Pokemon) -> PokemonBuild:
    # TODO: pokemon.maxhp does not work on opponent pokemon!
    max_hp = load_build_from_file(pokemon.species).get_most_likely_stats()["hp"] if pokemon.max_hp == 100 \
        else pokemon.max_hp



    return build_from_string(pokemon.species,
                             {
                                 "level": pokemon.level,
                                 "gender": "MALE" if pokemon.gender == PokemonGender.MALE
                                 else ("FEMALE" if pokemon.gender == PokemonGender.FEMALE else "NEUTRAL"),
                                 "item": pokemon.item if (pokemon.item is not None and pokemon.item != "unknown_item")
                                 else 'broken_item',
                                 "ability": pokemon.ability,
                                 "stats": {**pokemon.stats, **{"hp": max_hp}},
                                 "moves": "|".join(pokemon.moves)
                             })


def pokemon_from_build(build: PokemonBuild) -> Gen8Pokemon:
    """Creates a Pokémon described by the given build"""
    pokemon = Gen8Pokemon(species=build.species)
    pokemon._level = build.level
    pokemon.ability = build.get_most_likely_ability()
    pokemon._gender = PokemonGender.MALE if build.gender == "male" \
        else (PokemonGender.FEMALE if build.gender == "female" else PokemonGender.NEUTRAL)
    pokemon.item = build.get_most_likely_item()
    pokemon._last_request["stats"] = build.get_most_likely_stats()
    pokemon._moves = build.get_most_likely_moves()
    pokemon._current_hp = build.get_most_likely_stats()["hp"]
    pokemon._max_hp = pokemon._current_hp
    return pokemon

def clone_pokemon(pokemon: Gen8Pokemon) -> Pokemon:
    p = Gen8Pokemon(species=pokemon.species)
    p._level = pokemon.level
    p.ability = pokemon.ability
    p._gender = pokemon.gender
    p.item = pokemon.item
    p._moves = [Move(m) for m in pokemon.moves],
    pokemon._last_request["stats"] = build_from_pokemon(pokemon).get_most_likely_stats()
    p._current_hp = pokemon.current_hp_fraction * build_from_pokemon(pokemon).get_most_likely_stats()["hp"]
    p._max_hp = pokemon.max_hp
    p._boosts = pokemon.boosts

    return pokemon
