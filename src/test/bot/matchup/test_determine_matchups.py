import unittest

from poke_env.environment.battle import Battle

from pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.matchup.determine_matchups import determine_matchups, get_optimal_moves
from src.pokemon.data_handling.util.pokemon_creation import load_pokemon_from_file, load_build_from_file


class TestDetermineMatchup(unittest.TestCase):

    def test_determine_matchup(self):
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

        determine_matchups(battle, {names_team_p2[p]: builds_p2[p] for p in range(len(names_team_p2))})

    def test_get_optimal_moves(self):

        build1 = load_build_from_file("absol")
        build2 = load_build_from_file("latios")

        print(f'\n\nMoves of {build1.species}: {build1.get_most_likely_moves()}')
        print(f'Moves of {build2.species}: {build2.get_most_likely_moves()}')

        d = DamageCalculator()

        optimal_moves_absol = get_optimal_moves(build1, build2, build1.get_most_likely_moves(), 4, d)
        optimal_moves_latios = get_optimal_moves(build2, build1, build2.get_most_likely_moves(), 4, d)




if __name__ == "__main__":
    unittest.main()
