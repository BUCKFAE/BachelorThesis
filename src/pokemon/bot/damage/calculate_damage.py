from poke_env.environment.move import Move
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.status import Status
from poke_env.environment.weather import Weather


def calculate_damage(
        move: Move,
        attacker: Pokemon,
        defender: Pokemon,
        level: int,
        targets: int,
        weather: Weather,
        burned: bool,
        badge: int = 1.0):

    # TODO: Calculate stats
    ad = 1

    p1 = ((2 * level) / 5) + 2
    p2 = ((p1 * move.base_power * ad) / 50) + 2

    weather_mod = calculate_weather_multiplier(weather, move)
    stab_mod = calculate_stab_multiplier(attacker, move)
    brn_mod = calculate_burn_modifier(attacker, move)

    return p2 * targets * weather_mod * badge * stab_mod * brn_mod


def calculate_weather_multiplier(weather: Weather, move: Move) -> float:
    is_rainy = weather == Weather.RAINDANCE
    is_sunny = weather == Weather.SUNNYDAY

    if move.type == PokemonType.WATER and is_rainy:
        return 1.5
    if move.type == PokemonType.FIRE and is_sunny:
        return 1.5
    if move.type == PokemonType.FIRE and is_rainy:
        return 0.5
    if move.type == PokemonType.WATER and is_sunny:
        return 0.5

    return 1.0


def calculate_stab_multiplier(attacker: Pokemon, move: Move) -> float:
    return 1.5 if attacker.type_1 == move.type or attacker.type_2 == move.type else 1


def calculate_type_multiplier(defender: Pokemon, pkm_type: PokemonType) -> float:
    return pkm_type.damage_multiplier(defender.type_1, defender.type_2)


def calculate_stat_multiplier(move: Move) -> float:
    # TODO: Include stats in calculation!
    return 1.0


def calculate_burn_modifier(attacker: Pokemon, move: Move) -> float:
    if attacker.status == Status.BRN:
        if move.category == MoveCategory.PHYSICAL:
            if attacker.ability == "Guts":
                return 1
            return 0.5
    return 1
