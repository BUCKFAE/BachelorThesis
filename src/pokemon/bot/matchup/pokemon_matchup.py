"""Stores matchup information of two Pokemon"""
from src.pokemon import logger


class PokemonMatchup:

    def __init__(self,
                 species_p1: str,
                 species_p2: str):
        logger.info(f'Created matchup: {species_p1} vs {species_p2}')