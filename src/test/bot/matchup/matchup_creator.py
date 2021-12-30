"""Generates a List of PokemonMatchups that are used for testing"""
from typing import List

from poke_env.environment.battle import Battle
from singleton_decorator import singleton

from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.pokemon.data_handling.util.pokemon_creation import load_pokemon_from_file, load_build_from_file


@singleton
class MatchupCreator:
    _matchups = None

    def __init__(self, count: int = 3):
        if self._matchups is None:
            battle = Battle('test_battle_tag', 'buckfae', None, False)

            # Creating teams
            names_team_p1 = ["charizard", "salamence", "kyogre"]
            names_team_p2 = ["roserade", "luxray", "garchomp"]

            pokemon_p1 = [load_pokemon_from_file(p) for p in names_team_p1]

            pokemon_p2 = [load_pokemon_from_file(p) for p in names_team_p2]
            builds_p2 = [load_build_from_file(p) for p in names_team_p2]

            battle._available_switches = pokemon_p1
            battle._active_pokemon = pokemon_p1[0]

            battle._opponent_team = {names_team_p2[p]: pokemon_p2[p] for p in range(len(names_team_p2))}

            self._matchups = determine_matchups(battle,
                                                {names_team_p2[p]: builds_p2[p] for p in range(len(names_team_p2))})

    def get_test_matchups(self) -> List[PokemonMatchup]:
        assert self._matchups is not None
        return self._matchups
