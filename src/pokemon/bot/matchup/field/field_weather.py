"""All possible weather conditions"""
from enum import Enum


class FieldWeather(Enum):
    DEFAULT = 0
    SUN = 1
    RAIN = 2
    SAND = 3
    HAIL = 4
    HARSH_SUNSHINE = 5
    HEAVY_RAIN = 6
    STRONG_WINDS = 7
