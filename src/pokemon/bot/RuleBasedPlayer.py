import asyncio
from typing import Tuple

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.status import Status
from poke_env.environment.weather import Weather
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player
import sys

from poke_env.player.random_player import RandomPlayer

from src.pokemon.bot.RandomInformationPlayer import RandomInformationPlayer
from src.pokemon.bot.pokemon_build import PokemonBuild


def calculate_damage(battle: AbstractBattle, move: Move) -> float:
    if move.base_power == 0:
        return 0

    level = battle.active_pokemon.level
    power = move.base_power
    ad = calculate_stat_multiplier(move)  # TODO
    targets = 1  # This bot can only play single battles
    weather = calculate_weather_multiplier(battle, move)
    badge = 1.0  # Generation 2 only
    critical = 1.0  # TODO
    random = 1.0  # TODO
    stab = calculate_stab_multiplier(battle.active_pokemon, move)
    type_mod = calculate_type_multiplier(battle.opponent_active_pokemon, move.type)
    burn = calculate_burn_modifier(battle.active_pokemon, move)
    other = 1  # TODO

    p1 = ((2 * level) / 5) + 2
    p2 = ((p1 * power * ad) / 50) + 2
    return p2 * targets * weather * badge * critical * random * stab * type_mod * burn * other


def calculate_burn_modifier(attacker: Pokemon, move: Move) -> float:
    if attacker.status == Status.BRN:
        if move.category == MoveCategory.PHYSICAL:
            if attacker.ability == "Guts":
                return 1
            return 0.5
    return 1


def calculate_type_multiplier(defender: Pokemon, pkm_type: PokemonType) -> float:
    return pkm_type.damage_multiplier(defender.type_1, defender.type_2)


def calculate_stab_multiplier(attacker: Pokemon, move: Move) -> float:
    return 1.5 if attacker.type_1 == move.type or attacker.type_2 == move.type else 1


def calculate_weather_multiplier(battle: AbstractBattle, move: Move) -> float:
    is_rainy = any([w == Weather.RAINDANCE for w in battle.weather.keys()])
    is_sunny = any([w == Weather.SUNNYDAY for w in battle.weather.keys()])

    if move.type == PokemonType.WATER and is_rainy:
        return 1.5
    if move.type == PokemonType.FIRE and is_sunny:
        return 1.5
    if move.type == PokemonType.FIRE and is_rainy:
        return 0.5
    if move.type == PokemonType.WATER and is_sunny:
        return 0.5

    return 1.0


def calculate_stat_multiplier(move: Move) -> float:
    # TODO: Include stats in calculation!
    return 1.0


def get_best_switch(battle: AbstractBattle) -> Tuple[Pokemon, int]:
    best_switch = (None, 0)

    for curr in battle.available_switches:
        best_move = 0
        for move in curr.moves:
            dmg = calculate_damage(battle, curr.moves[move])
            if dmg >= best_move:
                best_move = dmg
        if best_move >= best_switch[1]:
            best_switch = (curr, best_move)

    return best_switch


def get_pokemon_vs_pokemon_type_mod(p1: Pokemon, p2: Pokemon) -> float:
    mod = calculate_type_multiplier(p1, p2.type_2) if p2.type_2 is not None else 1
    return calculate_type_multiplier(p1, p2.type_1) * mod


class RuleBasedPlayer(Player):
    # Storing all information we have of the enemy pokemon
    enemy_pokemon = {}

    timer = 0

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        self.update_enemy_information(battle)

        self.timer += 1
        if self.timer == 10:
            print(battle.opponent_team)


        # print("Available Moves: {}".format(battle.available_moves))

        # Calculating expected damages
        expected_damages = {}
        best_move = None
        if battle.available_moves:
            for move in battle.available_moves:
                dmg = calculate_damage(battle, move)
                expected_damages[move] = (dmg, move.self_boost)

            # print(expected_damages)
            best_move = max(expected_damages.keys(), key=lambda m: expected_damages[m][0])

        if len(battle.available_switches) >= 1:
            best_switch = get_best_switch(battle)

            if best_switch is not None:

                if best_move is None or best_switch[1] > expected_damages[best_move][0] * 2:
                    return self.create_order(best_switch[0])

        # print(f"Active boosts: {battle.active_pokemon.boosts}")

        # Boosting to stage 1
        for move in battle.available_moves:
            # print(f"{move.self_boost=}")
            if move.self_boost:
                for att, bst in move.self_boost.items():
                    if bst > 0 and battle.active_pokemon.boosts[att] < 1:
                        # print(f"Using boosting move to boost {att} by {bst}!")
                        return self.create_order(move)

        # print(f"Attacking: {best_move}")

        # TODO: Fix this, please
        if best_move is None:
            print("NOTHING WAS GOOD")
            return self.choose_random_move(battle)

        return self.create_order(best_move)

    def update_enemy_information(self, battle: AbstractBattle):

        for pokemon in battle.opponent_team:
            if pokemon not in self.enemy_pokemon.keys():
                self.enemy_pokemon[pokemon] = PokemonBuild(pokemon.split()[1], battle.opponent_team[pokemon].level)

async def main():
    p1 = RuleBasedPlayer(battle_format="gen8randombattle")
    p2 = RandomInformationPlayer(battle_format="gen8randombattle")

    await p1.battle_against(p2, n_battles=1)

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Random")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
