import re
import subprocess
from math import floor
from typing import Tuple, Dict, Optional

from poke_env.environment import status
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
from src.pokemon.data_handling.abilities.convert_ability import AbilityTranslator
from src.pokemon.data_handling.items.item_to_calc_item import ItemTranslator


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

        # Poke-Env returns the actual HP for the own pokemon, but a percentage value
        # for the enemy pokemon. Therefore, the HP stat has to be converted before
        # getting passed into the damage calculator. There is no Pokemon with an
        # HP stat of 100

        hp_error_msg = 'A pokemon in the Damage calculator had max_hp == 100. This is probably because ' \
                       'it was passed directly from battle to the damage calculator. Please clone a Pokemon ' \
                       'from the battle before passing it to calculate_damage. This is required as poke-env ' \
                       'only knows the HP percentage of an enemy Pokemon. The clone Method assigns the Pokemon ' \
                       'the correct (estimate) hp stat.'

        if attacker_pokemon is not None:
            assert attacker_pokemon.max_hp != 100, hp_error_msg
        if defender_pokemon is not None:
            assert defender_pokemon.max_hp != 100, hp_error_msg

        # Boosts for attacker
        boosts_attacker = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "hp": 0} if attacker_pokemon is None else \
            {**attacker_pokemon.boosts, **{"hp": 0}}

        # Boosts for defender
        boosts_defender = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "hp": 0} if defender_pokemon is None else \
            {**defender_pokemon.boosts, **{"hp": 0}}

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
        attacker_base_stats = re.sub("\'", "\"", str(attacker_build.base_stats))
        defender_base_stats = re.sub("\'", "\"", str(defender_build.base_stats))

        # Item
        it = ItemTranslator()
        attacker_item = it.item_to_calc_item(attacker_build.get_most_likely_item() if attacker_pokemon is None
                                                                                   or attacker_pokemon.item == 'unknown_item' else attacker_pokemon.item)
        defender_item = it.item_to_calc_item(defender_build.get_most_likely_item() if defender_pokemon is None
                                                                                   or defender_pokemon.item == 'unknown_item' else defender_pokemon.item)
        logger.info(type(attacker_item))
        logger.info(f'{attacker_item=}')
        logger.info(f'{defender_item=}')

        # HP
        attacker_hp = attacker_build.get_most_likely_stats()["hp"] if attacker_pokemon is None \
            else round(attacker_build.get_most_likely_stats()["hp"] * attacker_pokemon.current_hp_fraction)
        defender_hp = defender_build.get_most_likely_stats()["hp"] if defender_pokemon is None \
            else round(defender_build.get_most_likely_stats()["hp"] * defender_pokemon.current_hp_fraction)

        # Status
        attacker_status = "" if attacker_pokemon is None else _extract_status_from_pokemon(attacker_pokemon)
        defender_status = "" if defender_pokemon is None else _extract_status_from_pokemon(defender_pokemon)

        # Ability
        at = AbilityTranslator()
        attacker_ability = at.ability_to_calc_ability(attacker_build.get_most_likely_ability())
        defender_ability = at.ability_to_calc_ability(defender_build.get_most_likely_ability())

        # Dynamax
        attacker_is_dynamaxed = str(False if attacker_pokemon is None else attacker_pokemon.is_dynamaxed)
        defender_is_dynamaxed = str(False if defender_pokemon is None else defender_pokemon.is_dynamaxed)

        # Arguments that will be passed to the cli tool
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

        # TODO: Aegislash has a different form in poke-env when not active.
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
        # print(f'{calc_input=}')
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

        # Status after the attack
        status_attacker = move.status if move.target == 'allySide' else None
        status_defender = move.status if move.target == 'normal' else None

        # Status won't be overridden if the Pokémon already has a status effect
        status_attacker = attacker_pokemon.status \
            if (attacker_pokemon is not None and attacker_pokemon.status is not None) else status_attacker
        status_defender = defender_pokemon.status \
            if (defender_pokemon is not None and defender_pokemon.status is not None) else status_defender

        # Recoil
        damage_taken_attacker = round((sum(ranges) / len(ranges)) * move.recoil)
        damage_taken_attacker += floor(attacker_build.get_most_likely_stats()["hp"] / 10
                                       if attacker_item == 'Life Orb' else 0)

        # Healing attacker
        damage_healed_attacker = move.heal * attacker_build.get_most_likely_stats()["hp"]

        # Healing defender
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
            damage_healed_defender=damage_healed_defender,
            new_status_attacker=status_attacker,
            new_status_defender=status_defender
        )

        return move_result


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
        else:
            old_field.field_side_p2.light_screen = True
        return old_field
    elif side_condition == 'spikes':
        if side == 'allySide':
            old_field.field_side_p1.spikes_amount += 1
        else:
            old_field.field_side_p2.spikes_amount += 1
    else:
        pass
        # TODO: Implement other field conditions
        # logger.critical(f'Field condition {side_condition} is not yet implemented!')
        # raise NotImplementedError(f'Field condition {side_condition} is not yet implemented!')


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
