import json
import signal
import subprocess
import unittest
import os

from poke_env.environment.move import Move

from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator, extract_evs_ivs_from_build, \
    get_total_stat
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild


class TestDamageCalculator(unittest.TestCase):

    def test_calculate_damage(self):
        """Testing the expected damage a Pokémon will deal to another Pokémon"""

        # Salamence
        build1 = PokemonBuild("Salamence", 76, "MALE", "heavydutyboots", "moxie")
        build1._possible_builds = [(
            {"ability": "moxie",
             "stats": {"hp": 269, "atk": 249, "def": 166, "spa": 211, "spd": 166, "spe": 196},
             "gender": "male", "item": "heavydutyboots", "level": 76,
             "moves": "dragondance|dualwingbeat|earthquake|outrage"}, 1)]

        # Charizard
        build2 = PokemonBuild("Charizard", 82, "MALE", "heavydutyboots", "solarpower")
        build2._possible_builds = [(
            {"ability": "solarpower",
             "stats": {"hp": 262, "atk": 185, "def": 175, "spa": 226, "spd": 187, "spe": 211},
             "gender": "male",
             "item": "heavydutyboots",
             "level": 82,
             "moves": "airslash|earthquake|fireblast|roost"}, 1)]

        # No modifiers

        d = DamageCalculator()

        # Outrage
        outrage_damage = d.calculate_damage(build1, build2, Move("outrage"), None, None, None)
        assert outrage_damage == [141, 142, 144, 145, 147, 148, 151, 153, 154, 156, 157, 159, 160, 162, 163, 166]

        # Earthquake
        outrage_damage = d.calculate_damage(build1, build2, Move("earthquake"), None, None, None)
        assert outrage_damage == [0]

        # Boosted
        boosts_attacker = {"atk": 4, "def": 2, "spa": -1, "spd": 4, "spe": 4}
        boosts_defender = {"atk": -2, "def": 2, "spa": -4, "spd": 2, "spe": -5}
        outrage_damage = d.calculate_damage(build1, build2, Move("outrage"), None, boosts_attacker, boosts_defender)
        assert outrage_damage == [210, 211, 214, 217, 219, 222, 225, 226, 229, 232, 234, 237, 240, 241, 244, 247]

    def _test_validate_builds(self):
        """Ensures that we can get extract the evs and ivs of every known Pokémon"""

        validated_pokemon = 0
        validated_builds = 0

        for path, _, files in os.walk("src/data/generated"):
            for name in files:
                assert name.endswith(".txt")

                species = name.removesuffix(".txt")

                # TODO: Broken because of form
                if species == "wishiwashi" or species == "lycanroc":
                    continue

                with open(os.path.join(path, species) + ".txt") as replay_file:

                    for build_string in [b.strip() for b in replay_file.readlines() if b.strip()]:
                        build = json.loads(build_string.split(" - ")[1])

                        pokemon_build = PokemonBuild(species,
                                                     build["level"],
                                                     build["gender"].upper(),
                                                     build["item"],
                                                     build["ability"])

                        # Removing all invalid builds
                        pokemon_build._possible_builds = [b for b in pokemon_build._possible_builds
                                                          if b[0]["stats"] == build["stats"]]

                        # Getting assumed evs and ivs for the Pokémon
                        evs, ivs = extract_evs_ivs_from_build(pokemon_build)

                        # Ensuring the assumed stats match the actual stat
                        for stat in build["stats"]:
                            calculated_stat = get_total_stat(pokemon_build.base_stats, evs, ivs, build["level"], stat)
                            assert calculated_stat == build["stats"][stat]

                        validated_builds += 1
                validated_pokemon += 1
        print(f"Validated {validated_builds} builds of {validated_pokemon} pokemon")


if __name__ == "__main__":
    unittest.main()
