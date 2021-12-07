import re


def convert_species_to_file_name(species: str) -> str:
    return re.sub("[^a-z0-9]", "", species.split(":", maxsplit=1)[::-1][0].lower())
