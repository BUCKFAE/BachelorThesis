import unittest

from src.pokemon import logger
from src.pokemon.bot.matchup.field.field_side import FieldSide
from src.pokemon.bot.matchup.field.field_state import FieldState, battle_to_field, move_to_field_state, \
    switch_in_to_field_state
from src.pokemon.bot.matchup.field.field_terrain import FieldTerrain
from src.pokemon.bot.matchup.field.field_weather import FieldWeather


class TestFieldState(unittest.TestCase):

    def test_field_state(self):

        field1 = FieldState(
            FieldTerrain.GRASSY_TERRAIN,
            FieldWeather.SUN,
            FieldSide(),
            FieldSide())

        field2 = FieldState(
            FieldTerrain.GRASSY_TERRAIN,
            FieldWeather.RAIN,
            FieldSide(),
            FieldSide()
        )

        # Testing basic properties of dataclasses
        assert field1.terrain == FieldTerrain.GRASSY_TERRAIN
        assert field2.terrain == FieldTerrain.GRASSY_TERRAIN
        assert field1.weather == FieldWeather.SUN
        assert field2.weather == FieldWeather.RAIN

    def test_battle_to_field(self):
        # TODO
        raise NotImplementedError

    def test_move_to_field_state(self):
        # TODO
        raise NotImplementedError

    def test_switch_in_to_field_state(self):
        # TODO
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
