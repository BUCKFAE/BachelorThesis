import unittest

from src.pokemon.data_handling.util.pokemon_creation import load_build_from_file, pokemon_from_build, clone_pokemon


class TestPokemonCreation(unittest.TestCase):

    def test_pokemon_from_build(self):

        build = load_build_from_file("charizard")
        pokemon = pokemon_from_build(build)

        # Ensuring the Pokémon has correct stats
        assert pokemon.max_hp == 262
        assert pokemon.current_hp == 262
        assert pokemon.current_hp_fraction == 1
        assert pokemon.item == 'heavydutyboots'
        assert pokemon.level == 82
        assert all([move in pokemon.moves.keys() for move in ['airslash', 'fireblast', 'focusblast', 'roost']])
        assert pokemon.ability == 'solarpower'
        assert pokemon.stats['hp'] == 262
        assert pokemon.stats['atk'] == 142
        assert pokemon.stats['def'] == 175
        assert pokemon.stats['spd'] == 187
        assert pokemon.stats['spe'] == 211

    def test_clone_pokemon(self):
        """Testing cloning of Pokémon
        If an *enemy* Pokemon is cloned, it's max-hp and current-hp stat need to be adjusted
        as well, otherwise they can't be fed into the damage calculator
        """
        b1 = load_build_from_file('charizard')
        p1 = pokemon_from_build(b1)
        p2 = pokemon_from_build(b1)

        # Making own charizard loose hp
        p1._current_hp = 131
        assert p1.current_hp == 131
        assert p1.current_hp_fraction == 0.5

        # Enemy charizard loose hp
        p2._max_hp = 100
        p2._current_hp = 50
        assert p2.max_hp == 100
        assert p2.current_hp == 50
        assert p2.current_hp_fraction == 0.5

        # Cloning
        clone_1 = clone_pokemon(p1, b1)
        clone_2 = clone_pokemon(p2, b1)

        for charizard in [clone_1, clone_2]:
            # Ensuring the Pokémon has correct stats
            assert charizard.max_hp == 262
            assert charizard.current_hp == 131
            assert charizard.current_hp_fraction == 0.5
            assert charizard.item == 'heavydutyboots'
            assert charizard.level == 82
            assert all([move in charizard.moves.keys() for move in ['airslash', 'fireblast', 'focusblast', 'roost']])
            assert charizard.ability == 'solarpower'
            assert charizard.stats['hp'] == 262
            assert charizard.stats['atk'] == 142
            assert charizard.stats['def'] == 175
            assert charizard.stats['spd'] == 187
            assert charizard.stats['spe'] == 211




