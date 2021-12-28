"""Represents the current state of the field"""
from dataclasses import dataclass

from poke_env.environment.abstract_battle import AbstractBattle

from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.field.field_side import FieldSide
from src.pokemon.bot.matchup.field.field_terrain import FieldTerrain
from src.pokemon.bot.matchup.field.field_weather import FieldWeather


@dataclass
class FieldState:
    """Represents the state of the field at a given turn"""

    def __init__(self,
                 terrain: FieldTerrain,
                 weather: FieldWeather,
                 field_side_p1: FieldSide,
                 field_side_p2: FieldSide,
                 is_magic_room: bool = False,
                 is_wonder_room: bool = False,
                 is_gravity: bool = False):
        self.terrain = terrain
        self.weather = weather
        self.field_side_p1 = field_side_p1
        self.field_side_p2 = field_side_p2
        self.is_magic_room = is_magic_room
        self.is_wonder_room = is_wonder_room
        self.is_gravity = is_gravity


def battle_to_field(battle: AbstractBattle) -> FieldState:
    """Converts the field of an ongoing battle to a FieldState"""
    raise NotImplementedError


def move_to_field_state(prev_field_state: FieldSide, side: int, move: str) -> FieldState:
    """Returns the field after the move was executed by player"""
    assert side == 1 or side == 2
    raise NotImplementedError


def switch_in_to_field_state(prev_field_state: FieldSide, side: int, pokemon_build: PokemonBuild) -> FieldState:
    """Returns the field after the Pokemon was switched in
    Example: Pokemon that change the weather upon being switched in
    """
    raise NotImplementedError
