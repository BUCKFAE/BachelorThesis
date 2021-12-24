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
    s = re.sub("mimikyubusted", "mimikyu", s)
    s = re.sub("eiscuenoice", "eiscue", s)

    s = re.sub("[^a-z0-9]", "", s)
    return s
