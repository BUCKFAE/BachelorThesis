import logging
import re


def convert_species_name(species: str) -> str:
    """
    Converts the name of the species into the corresponding name used in poke-env
    """
    logging.debug(f"Original species: {species}")
    s = species.lower()

    # TODO: This may need to be improved later
    s = re.sub("gmax", "", s)
    s = re.sub("galar", "", s)
    s = re.sub("wishiwashischool", "wishiwashi", s)
    s = re.sub("aegislashblade", "aegislash", s)
    s = re.sub("darmanitanzen", "darmanitan", s)

    s = re.sub("[^a-z0-9]", "", s)
    logging.debug(f"Species name after conversion: {s}")
    return s


