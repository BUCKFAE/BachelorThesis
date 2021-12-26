import re
import subprocess
from typing import Tuple, Dict, Optional, List

from poke_env.environment import status
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.pokemon_type import PokemonType
from singleton_decorator import singleton

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.field.field_side import FieldSide
from src.pokemon.bot.matchup.field.field_state import FieldState
from src.pokemon.bot.matchup.field.field_terrain import FieldTerrain
from src.pokemon.bot.matchup.field.field_weather import FieldWeather
from src.pokemon.bot.matchup.move_result import MoveResult
from src.pokemon.config import NODE_DAMAGE_CALCULATOR_PATH
from src.pokemon.data_handling.abilities.convert_ability import get_calculator_ability


@singleton
class DamageCalculator:
    _cli_tool = None

    def __init__(self):
        if self._cli_tool is None:
            self._cli_tool = subprocess.Popen(["npm run start"],
                                              cwd=NODE_DAMAGE_CALCULATOR_PATH,
                                              stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    def calculate_damage(
            self,
            attacker_build: PokemonBuild,
            defender_build: PokemonBuild,
            move: Move,
            attacker_pokemon: Optional[Pokemon] = None,
            defender_pokemon: Optional[Pokemon] = None,
            field: Optional[FieldState] = None) -> MoveResult:
        # TODO: This has to include current states of the Pokemon

        # Boosts for attacker
        boosts_attacker = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "hp": 0}
        if attacker_pokemon is not None:
            boosts_attacker = attacker_pokemon.boosts

        # Boosts for defender
        boosts_defender = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "hp": 0}
        if defender_pokemon is not None:
            boosts_defender = defender_pokemon.boosts

        # Getting EVs and IVs for both Pokemon
        attacker_evs, attacker_ivs = extract_evs_ivs_from_build(attacker_build)
        defender_evs, defender_ivs = extract_evs_ivs_from_build(defender_build)

        # TypeScript expects double instead of single quotes
        attacker_evs = re.sub("\'", "\"", str(attacker_evs))
        attacker_ivs = re.sub("\'", "\"", str(attacker_ivs))
        defender_evs = re.sub("\'", "\"", str(defender_evs))
        defender_ivs = re.sub("\'", "\"", str(defender_ivs))

        # Boosts
        boosts_attacker = re.sub("\'", "\"", str(boosts_attacker))
        boosts_defender = re.sub("\'", "\"", str(boosts_defender))

        # Base stats
        attacker_base_stats = re.sub("\"", "\'", str(attacker_build.base_stats))
        defender_base_stats = re.sub("\"", "\'", str(defender_build.base_stats))

        # Item
        # TODO: Get item from Pokemon directly
        attacker_item = attacker_build.get_most_likely_item()
        defender_item = defender_build.get_most_likely_item()

        # HP
        attacker_hp = attacker_build.get_most_likely_stats()["hp"] if attacker_pokemon is None \
            else attacker_pokemon.current_hp
        defender_hp = defender_build.get_most_likely_stats()["hp"] if defender_pokemon is None \
            else defender_pokemon.current_hp

        # Status
        attacker_status = "" if attacker_pokemon is None else _extract_status_from_pokemon(attacker_pokemon)
        defender_status = "" if defender_pokemon is None else _extract_status_from_pokemon(defender_pokemon)

        # Ability
        # TODO: Get ability from Pokemon directly
        attacker_ability = get_calculator_ability(attacker_build.get_most_likely_ability())
        defender_ability = get_calculator_ability(defender_build.get_most_likely_ability())

        # Dynamax
        # noinspection PyProtectedMember
        attacker_is_dynamaxed = str(False if attacker_pokemon is None else attacker_pokemon.is_dynamaxed)
        # noinspection PyProtectedMember
        defender_is_dynamaxed = str(False if defender_pokemon is None else defender_pokemon.is_dynamaxed)

        # TODO: Include current state of both Pokemon (like BRN, lost HP)
        calculator_args = [
            attacker_build.species,
            attacker_build.species,
            "M" if attacker_build.gender == "male" else ("F" if attacker_build.gender == "female" else "N"),
            attacker_build.level,
            attacker_base_stats,
            attacker_ivs,
            attacker_evs,
            boosts_attacker,
            "Hardy",  # All Pokémon have neutral nature
            attacker_ability,
            attacker_item if attacker_item != 'broken_item' else '',
            attacker_status,  # No status
            attacker_hp,
            attacker_is_dynamaxed,
            defender_build.species,
            defender_build.species,
            "M" if defender_build.gender == "Male" else ("F" if defender_build.gender == "Female" else "N"),
            defender_build.level,
            defender_base_stats,
            defender_ivs,
            defender_evs,
            boosts_defender,
            "Hardy",  # All Pokémon have neutral nature
            defender_ability,
            defender_item if defender_item != 'broken_item' else '',
            defender_status,  # No status
            defender_hp,
            defender_is_dynamaxed,
            move.id
        ]

        # TODO: Fix Aegislash
        if "aegislash" == attacker_build.species:
            calculator_args[0] = 'aegislashblade'
        if "aegislash" == defender_build.species:
            calculator_args[14] = 'aegislashblade'

        # Fixing Gastrodon
        # Poke-Env uses 'gastrodon' and 'gastrodoneast' for both variants
        # The damage-calculator uses 'gastrodon' for both variants
        if attacker_build.species == 'gastrodoneast':
            calculator_args[0] = 'gastrodon'
        if defender_build.species == 'gastrodoneast':
            calculator_args[14] = 'gastrodon'

        # There are multiple pikachu species, they all have the same base stats and are handled
        # identically by the damage calculator
        if "pikachu" in attacker_build.species:
            calculator_args[0] = "pikachu"
        if "pikachu" in defender_build.species:
            calculator_args[14] = "pikachu"

        calculator_args[0] = calculator_args[0].capitalize()
        calculator_args[14] = calculator_args[14].capitalize()

        calc_input = (";;".join([str(i) for i in calculator_args]) + "\n").encode()

        self._cli_tool.stdin.write(calc_input)
        self._cli_tool.stdin.flush()

        # Getting output
        output = []
        while True:
            res = self._cli_tool.stdout.readline().decode().strip()
            if res == "DONE!":
                break
            output.append(res)

        print('\n'.join(output))

        # Getting the damage ranges
        res = [e for e in output if re.match("damage: [0-9]+,", e)]
        if res:
            res = res[0]
        else:
            start_index = output.index("damage: [")
            end_index = output[start_index:].index("],")
            res = "".join(output[start_index:start_index + end_index])
        ranges_text = re.sub("[^0-9,]", "", res)
        ranges = [int(i) for i in ranges_text.split(",") if i]

        # Field side 1
        field_side_p1 = FieldSide()

        # Field side 2
        field_side_p2 = FieldSide()

        # Creating field state
        field_state = FieldState(
            FieldTerrain.DEFAULT,
            FieldWeather.DEFAULT,
            field_side_p1,
            field_side_p2
        )

        # Modifying field state
        field_state = _side_condition_to_field(move.side_condition, field_state, move.deduced_target)

        # Recoil
        damage_taken_attacker = round((sum(ranges) / len(ranges)) * move.recoil)

        # Healing attacker
        damage_healed_attacker = move.heal * attacker_build.get_most_likely_stats()["hp"]

        damage_healed_defender = round(defender_build.get_most_likely_stats()["hp"] * 0.25) if \
            defender_ability == 'Water Absorb' and move.type == PokemonType.WATER else 0

        # Creating MoveResult
        move_result = MoveResult(
            species_p1=attacker_build.species,
            species_p2=defender_build.species,
            move=move.id,
            new_field_state=field_state,
            damage_taken_defender=ranges,
            damage_taken_attacker=damage_taken_attacker,
            damage_healed_attacker=damage_healed_attacker,
            damage_healed_defender=damage_healed_defender
        )

        return move_result

    def get_optimal_moves(
            self,
            attacker_build: PokemonBuild,
            attacker_pokemon: Optional[Pokemon],
            defender_build: PokemonBuild,
            defender_pokemon: Optional[Pokemon],
            battle: AbstractBattle) -> List[MoveResult]:
        # TODO: Account for disabled moves!!

        best_move = (None, -1)

        logger.info(f"Most likely moves for: {attacker.species}\n\t{attacker.get_most_likely_moves()}")

        for move in attacker.get_most_likely_moves():

            if not move.strip():
                logger.warning('The pokemon has no moves left, using struggle!')
                move = 'struggle'

            # TODO: Use expected damage instead (misses)
            damage_range = self.calculate_damage(
                attacker,
                defender,
                Move(move),
                battle,
                None,
                None
            )
            expected_damage = sum(damage_range) / len(damage_range)
            if expected_damage >= best_move[1]:
                best_move = (move, expected_damage)

        assert best_move[0] is not None
        assert best_move[1] >= 0

        raise NotImplementedError('This has to return MoveResults')


def extract_evs_ivs_from_build(pokemon: PokemonBuild) -> Tuple[Dict[str, int], Dict[str, int]]:
    assumed_ivs = {"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31}
    assumed_evs = {"hp": 85, "atk": 85, "def": 85, "spa": 85, "spd": 85, "spe": 85}

    # On some Pokémon these stats occur along a 31 iv stat
    possible_evs = [0, 48, 76, 80, 84]

    # Getting assumed ivs and evs
    for key, value in pokemon.get_most_likely_stats().items():

        # If the stat is not (31 / 85) it's (0, 0)
        if get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key) \
                != pokemon.get_most_likely_stats()[key]:
            assumed_ivs[key] = 0
            assumed_evs[key] = 0

            # Nether (31 / 85) nor (0 / 0)
            if get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key) \
                    != pokemon.get_most_likely_stats()[key]:

                for possible_ev in possible_evs:
                    assumed_ivs[key] = 31
                    assumed_evs[key] = possible_ev

                    res = get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key)
                    if res == pokemon.get_most_likely_stats()[key]:
                        break

            estimate = get_total_stat(pokemon.base_stats, assumed_evs, assumed_ivs, pokemon.level, key)

            if estimate != pokemon.get_most_likely_stats()[key]:

                # Handling wishiwashi
                if pokemon.species == "wishiwashi":
                    p = Pokemon(species="wishiwashischool")
                    if pokemon.base_stats != p.base_stats:
                        pokemon.base_stats = p.base_stats
                        return extract_evs_ivs_from_build(pokemon)

                ValueError(f"Stat \"{key}\" was not matching for \"{pokemon.species}\""
                           f"\n\texpected: {pokemon.get_most_likely_stats()[key]} actual: {estimate} ")

    return assumed_evs, assumed_ivs


def _get_evs(base: Dict[str, int], stats: Dict[str, int], ivs: Dict[str, int], level: int, stat: str) -> int:
    temp1 = int(((stats[stat] - 5) * 100) / level) - (2 * base[stat])
    return int(temp1 - (ivs[stat] / 4))


def _get_ivs(base: Dict[str, int], stats: Dict[str, int], evs: Dict[str, int], level: int, stat: str) -> int:
    temp1 = int(((stats[stat] - 5) * 100) / level) - (2 * base[stat])
    return (temp1 - evs[stat]) * 4


def _extract_status_from_pokemon(pokemon: Pokemon) -> str:
    if pokemon.status is None:
        return ''
    if pokemon.status == status.Status.BRN:
        return 'brn'
    if pokemon.status == status.Status.FRZ:
        return 'frz'
    if pokemon.status == status.Status.SLP:
        return 'slp'
    if pokemon.status == status.Status.FNT:
        return 'fnt'
    if pokemon.status == status.Status.PAR:
        return 'par'
    if pokemon.status == status.Status.PSN:
        return 'psn'
    if pokemon.status == status.Status.TOX:
        return 'tox'

    raise ValueError(f'Unknown status for Pokemon: {pokemon.status}')


def _side_condition_to_field(side_condition: str, old_field: FieldState, side: Optional[str]) -> FieldState:
    # No changes
    if not side_condition:
        return old_field

    # Light screen
    if side_condition == 'lightscreen':
        if side == 'allySide':
            old_field.field_side_p1.light_screen = True
        if side == 2:
            old_field.field_side_p2.light_screen = True
        return old_field
    else:
        raise NotImplementedError(f'Field condition {side_condition} is not yet implemented!')

def get_total_stat(base: Dict[str, int], evs: Dict[str, int], ivs: Dict[str, int], level: int, stat: str) -> int:
    # Different formula for HP stat
    if stat == "hp":

        # Shedinja
        if base["hp"] == 1:
            return 1

        temp1 = (2 * base[stat] + ivs[stat] + int(evs[stat] / 4)) * level
        return int(temp1 / 100) + level + 10

    temp1 = (2 * base[stat] + ivs[stat] + int(evs[stat] / 4)) * level
    return int(temp1 / 100) + 5
