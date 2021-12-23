"""All possible field terrain types"""
from enum import Enum


class FieldTerrain(Enum):
    DEFAULT = 0
    ELECTRIC_TERRAIN = 1
    GRASSY_TERRAIN = 2
    MISTY_TERRAIN = 3
    PSYCHIC_TERRAIN = 4
