import logging
import re


def convert_species_name(species: str) -> str:
    """
    Converts the name of the species into the corresponding name used in poke-env
    """
    s = species.lower()

    # Removing player name if present
    if "p1:" in s or "p2:" in s:
        s = s[4:]

    # TODO: This may need to be improved later
    #s = re.sub("gmax", "", s)
    #s = re.sub("galar", "", s)
    #s = re.sub("wishiwashischool", "wishiwashi", s)
    #s = re.sub("aegislashblade", "aegislash", s)
    #s = re.sub("darmanitanzen", "darmanitan", s)

    s = re.sub("[^a-z0-9]", "", s)
    return s


