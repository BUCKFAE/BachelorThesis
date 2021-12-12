import os
import unittest

from poke_env.environment.battle import Battle
from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.config import GENERATED_DATA_PATH
from src.pokemon.data_handling.util.pokemon_creation import load_pokemon_from_file, load_build_from_file


def _get_all_pokemon_names(limit=20):
    names = []
    for path, _, files in os.walk(GENERATED_DATA_PATH):
        for file in files:
            names.append(file.replace(".txt", ""))

    return names[:limit]


class TestDetermineMatchup(unittest.TestCase):

    def test_determine_matchup(self):

        battle = Battle('test_battle_tag', 'buckfae', None, False)

        names_team_p1 = _get_all_pokemon_names()
        names_team_p2 = ["espeon"]

        pokemon_p1 = [load_pokemon_from_file(p) for p in names_team_p1]

        pokemon_p2 = [load_pokemon_from_file(p) for p in names_team_p2]
        builds_p2 = [load_build_from_file(p) for p in names_team_p2]

        battle._team = pokemon_p1

        battle._opponent_team = {names_team_p2[p]: pokemon_p2[p] for p in range(len(names_team_p2))}

        determine_matchups(battle, {names_team_p2[p]: builds_p2[p] for p in range(len(names_team_p2))})


if __name__ == "__main__":
    unittest.main()
