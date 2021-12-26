import unittest

from poke_env.environment import status
from poke_env.environment.effect import Effect
from poke_env.environment.move import Move

from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.matchup.move_result import MoveResult
from src.pokemon.data_handling.util.pokemon_creation import load_build_from_file, pokemon_from_build


class TestDamageCalculator(unittest.TestCase):
    """Testing the Damage Calculator

    - Simple Attacking with no special effects [DONE]
    - Stat boosts (Swords Dance) [DONE]
    - Healing [DONE]
    - Recoil [DONE]
    - Status changes (BRN) [DONE]
    - Dynamax [DONE]
    - Abilities [DONE]
        - Levitate [DONE]
        - Water absorb [DONE]
    - Pokemon with different forms
        - Gastrodon
        - Wishiwashi - Transforming TODO
        - Zygarde - Transforming TODO
        - Shedinja - Transforming TODO
    - Changes to the field after the attack [DONE]
        - Reflect [DONE]
    - Damage through Weather TODO
    - Healing TODO
        - Leftovers TODO
        - Leech seed TODO
    - Items TODO
        - Life Orb TODO
        - Air ballon TODO
    """

    def test_damage_calculator_basic(self):
        """Tests a very basic example where Charizard attacks Salamence"""

        build1 = load_build_from_file("charizard")
        build2 = load_build_from_file("salamence")

        damage_calculator = DamageCalculator()

        # Air Slash
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("airslash"))
        assert res1.damage_taken_defender == [90, 91, 91, 93, 94, 94, 96, 97, 99, 99, 100, 102, 102, 103, 105, 106]

        # Earthquake
        res2: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("earthquake"))
        assert res2.damage_taken_defender == [0]

        # Fire Blast
        res3: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("fireblast"))
        assert res3.damage_taken_defender == [65, 66, 66, 67, 68, 69, 69, 70, 71, 72, 72, 73, 74, 75, 75, 77]

        # Focus Blast
        res4: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("focusblast"))
        assert res4.damage_taken_defender == [48, 48, 49, 49, 50, 50, 51, 51, 52, 53, 53, 54, 54, 55, 55, 56]

    def test_damage_calculator_stat_boosts(self):
        """Tests attack with stat boosts"""

        build1 = load_build_from_file("charizard")
        build2 = load_build_from_file("garchomp")
        pokemon1 = pokemon_from_build(build1)
        pokemon2 = pokemon_from_build(build2)

        # Increasing stats of charizard
        pokemon1.boosts["atk"] = 1
        pokemon1.boosts["def"] = 2
        pokemon1.boosts["spa"] = 3
        pokemon1.boosts["spd"] = 4
        pokemon1.boosts["spe"] = 5

        # Decreasing stats of garchomp
        pokemon2.boosts["atk"] = - 1
        pokemon2.boosts["def"] = - 2
        pokemon2.boosts["spa"] = - 3
        pokemon2.boosts["spd"] = - 4
        pokemon2.boosts["spe"] = - 5

        damage_calculator = DamageCalculator()

        # Charizard: Air Slash
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("airslash"),
                                                              attacker_pokemon=pokemon1, defender_pokemon=pokemon2)
        assert res1.damage_taken_defender == \
               [657, 664, 672, 681, 688, 696, 703, 711, 718, 727, 735, 742, 750, 757, 765, 774]


        # Charizard: Earthquake
        res2: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("earthquake"),
                                                              attacker_pokemon=pokemon1, defender_pokemon=pokemon2)
        assert res2.damage_taken_defender ==  \
               [175, 177, 179, 181, 183, 185, 187, 189, 191, 193, 195, 197, 199, 201, 203, 206]

        # Garchomp: Fire Blast
        res3: MoveResult = damage_calculator.calculate_damage(build2, build1, Move("fireblast"),
                                                              attacker_pokemon=pokemon2, defender_pokemon=pokemon1)
        assert res3.damage_taken_defender == [3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

        # Garchomp: Outrage
        res4: MoveResult = damage_calculator.calculate_damage(build2, build1, Move("outrage"),
                                                              attacker_pokemon=pokemon2, defender_pokemon=pokemon1)
        assert res4.damage_taken_defender == [43, 45, 45, 45, 46, 46, 46, 48, 48, 48, 49, 49, 49, 51, 51, 52]

    def test_damage_calculator_status_effect(self):
        build1 = load_build_from_file("weezinggalar")
        build2 = load_build_from_file("garchomp")
        pokemon1 = pokemon_from_build(build1)
        pokemon2 = pokemon_from_build(build2)

        damage_calculator = DamageCalculator()

        # Physical attack not burned
        res1: MoveResult = damage_calculator.calculate_damage(build2, build1, Move("firefang"))
        assert res1.damage_taken_defender == [32, 32, 33, 33, 33, 34, 34, 34, 35, 35, 36, 36, 36, 37, 37, 38]

        # Will-O-Wisp burns
        res2: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("willowisp"))
        assert res2.damage_taken_defender == [0]
        assert res2.new_status_defender == status.Status.BRN

        # Buring Garchomp
        pokemon1._status = status.Status.BRN

        # Physical attack burned
        res3: MoveResult = damage_calculator.calculate_damage(build2, build1, Move('firefang'),
                                                              attacker_pokemon=pokemon2)
        assert res3.damage_taken_defender == [16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 18, 18, 18, 18, 18, 19]

    def test_damage_calculator_healing_attacker(self):
        build1 = load_build_from_file("mewtwo")
        build2 = load_build_from_file("charizard")
        pokemon1 = pokemon_from_build(build1)

        # Mewtwo took damage
        pokemon1._current_hp = 136

        damage_calculator = DamageCalculator()

        # Recover on full HP Pokemon
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("recover"))
        assert res1.damage_healed_attacker == 136

    def test_damage_calculator_healing_defender(self):
        """Tests cases where the attacker heals the opponent"""

        build1 = load_build_from_file("lapras")
        build2 = load_build_from_file("blastoise")

        damage_calculator = DamageCalculator()

        # Lapras with Water absorb takes no damage from water moves, heals for 25% max HP
        res: MoveResult = damage_calculator.calculate_damage(build2, build1, Move("hydropump"))
        assert res.damage_taken_defender == [0]
        assert res.damage_healed_attacker == 182

    def test_damage_calculator_recoil(self):
        """Ensures recoil damage works correctly
        Recoil is always a fraction of the damage dealt. Here, we use the recoil of the expected damage dealt
        """

        build1 = load_build_from_file("hooh")
        build2 = load_build_from_file("charizard")

        damage_calculator = DamageCalculator()

        # Brave bird
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("bravebird"))
        assert res1.damage_taken_defender == \
               [121, 123, 124, 126, 127, 129, 130, 132, 133, 135, 136, 138, 139, 141, 142, 144]
        assert res1.damage_taken_attacker == 132.5

    def test_damage_calculator_levitate(self):
        """Ensures that levitate works correctly"""

        build1 = load_build_from_file("charizard")
        build2 = load_build_from_file("bronzong")
        pokemon2 = pokemon_from_build(build2)

        damage_calculator = DamageCalculator()

        # Earthquake (levitate)
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("earthquake"),
                                                              defender_pokemon=pokemon2)
        assert res1.damage_taken_defender == [0]

        # Air Slash
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("airslash"))
        assert res1.damage_taken_defender == [31, 32, 32, 33, 33, 33, 33, 34, 34, 35, 35, 36, 36, 36, 36, 37]

    def test_damage_calculator_field_changes(self):
        """Changes to the field after the attack"""

        build1 = load_build_from_file("wigglytuff")
        build2 = load_build_from_file("charizard")

        damage_calculator = DamageCalculator()

        # Light Screen
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("lightscreen"))
        assert res1.new_field_state.field_side_p1.light_screen

    def test_damage_calculator_dynamax(self):

        build1 = load_build_from_file("charizard")
        build2 = load_build_from_file("salamence")
        pokemon1 = pokemon_from_build(build1)

        # Dynamaxing Charizard
        pokemon1._effects[Effect.DYNAMAX] = True

        damage_calculator = DamageCalculator()

        # Air Slash
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("airslash"), pokemon1)
        assert res1.damage_taken_defender == \
               [154, 156, 159, 160, 162, 163, 166, 168, 169, 171, 172, 175, 177, 178, 180, 183]

        # Earthquake
        res2: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("earthquake"), pokemon1)
        assert res2.damage_taken_defender == [0]

        # Fireblast
        res3: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("fireblast"), pokemon1)
        assert res3.damage_taken_defender == [83, 84, 84, 86, 87, 87, 89, 90, 90, 92, 93, 93, 95, 96, 96, 98]

    def test_damage_calculator_gastrodon(self):

        build1 = load_build_from_file("gastrodon")
        build2 = load_build_from_file("gastrodoneast")

        damage_calculator = DamageCalculator()

        # Earthquake
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("earthquake"))
        res2: MoveResult = damage_calculator.calculate_damage(build2, build1, Move("earthquake"))
        assert res1.damage_taken_defender == \
            [105, 106, 108, 109, 109, 111, 112, 114, 115, 117, 117, 118, 120, 121, 123, 124]
        assert res2.damage_taken_defender == \
            [105, 106, 108, 109, 109, 111, 112, 114, 115, 117, 117, 118, 120, 121, 123, 124]

    def test_damage_calculator_gourgeist_venusaur(self):
        """This matchup used to return incorrect damage ranges."""

        build1 = load_build_from_file("gourgeistsuper")
        build2 = load_build_from_file("venusaur")

        damage_calculator = DamageCalculator()

        # Poltergeist
        res1: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("poltergeist"))
        assert res1.damage_taken_attacker \
               == [117, 118, 120, 120, 121, 123, 124, 126, 127, 129, 130, 132, 133, 135, 136, 138]

        # Power Whip
        res2: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("powerwhip"))
        assert res2.damage_taken_defender == [31, 32, 32, 33, 33, 33, 34, 34, 34, 35, 35, 36, 36, 36, 37, 37]

        # Shadow Sneak
        res3: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("shadowsneak"))
        assert res3.damage_taken_defender == [43, 45, 45, 45, 46, 46, 46, 48, 48, 48, 49, 49, 49, 51, 51, 52]

        # Will-O-Wisp
        res4: MoveResult = damage_calculator.calculate_damage(build1, build2, Move("willowisp"))
        assert res4.damage_taken_defender == [0]
        assert res4.new_status_defender == status.Status.BRN


if __name__ == "__main__":
    unittest.main()
