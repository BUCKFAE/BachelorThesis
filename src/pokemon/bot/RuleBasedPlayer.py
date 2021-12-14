import asyncio
import json
import sys
from typing import Dict

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player

from poke_env.player.random_player import RandomPlayer

from src.pokemon.bot.MaxDamagePlayer import MaxDamagePlayer
from src.pokemon.bot.RandomInformationPlayer import RandomInformationPlayer
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.data_handling.util.pokemon_creation import build_from_pokemon


class RuleBasedPlayer(Player):
    # Storing all information we have of the enemy Pokémon
    enemy_pokemon: Dict[str, PokemonBuild] = {}

    # Storing Matchup information
    matchups = {}

    damage_calculator = DamageCalculator()

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        print(f"Matchup: {battle.active_pokemon.species} vs {battle.opponent_active_pokemon.species}")

        own_species = battle.active_pokemon.species
        enemy_species = battle.opponent_active_pokemon.species

        # Updating information we gathered about the enemy team
        new_information_collected = self.update_enemy_information(battle)

        print(f"Items: {battle.active_pokemon.item} {self.enemy_pokemon[enemy_species].get_most_likely_item()}")

        # Determining matchup again if new information was gathered
        if new_information_collected or battle.active_pokemon.first_turn:
            # print(f"Getting matchups!")
            # Getting current Matchup
            self.matchups = determine_matchups(battle, self.enemy_pokemon)
            print(json.dumps(self.matchups, indent=4, sort_keys=True))

        # Checking if our current matchup is bad
        current_enemy_matchups = self.matchups[enemy_species]
        current_enemy_checks = current_enemy_matchups["checks"]
        current_enemy_counter = current_enemy_matchups["counter"]

        # Switching if we have to
        if not battle.available_moves:
            print(f"Forced to switch!")
            current_enemy_checks = [c for c in current_enemy_checks if c != own_species]
            current_enemy_counter = [c for c in current_enemy_counter if c != own_species]

            if len(current_enemy_checks) > 0:
                print(f"Switching to check: {current_enemy_checks[0]}")
                check = [p for p in battle.available_switches if p.species == current_enemy_checks[0]][0]
                return self.create_order(check)
            elif len(current_enemy_counter) > 0:
                print(f"Switching to counter: {current_enemy_counter[0]}")
                counter = [p for p in battle.available_switches if p.species == current_enemy_counter[0]][0]
                return self.create_order(counter)
            else:
                print(f"No good switch found, switching random")
                return self.choose_random_move(battle)

        # Getting HP
        own_hp = battle.active_pokemon.current_hp
        enemy_hp = self.enemy_pokemon[enemy_species].get_remaining_hp(
            battle.opponent_active_pokemon.current_hp_fraction)

        # Testing if we can kill the opponent this turn
        print(f"HP: {own_hp} - {enemy_hp}")

        # Getting Speed
        own_speed = battle.active_pokemon.stats["spe"]
        enemy_speed = self.enemy_pokemon[enemy_species].get_most_likely_stats()["spe"]
        print(f"Speed: {own_speed} - {enemy_speed}")

        # TODO: Better to account for usable moves here
        own_pokemon_build = build_from_pokemon(battle.active_pokemon)
        own_pokemon_build._possible_builds[0][0]["moves"] = \
            "|".join([m for m in own_pokemon_build._possible_builds[0][0]["moves"].split("|") if m in
                      [m.id for m in battle.available_moves]])

        # Getting the most damaging moves
        best_own_move = self.damage_calculator.get_most_damaging_move(
            own_pokemon_build,
            self.enemy_pokemon[enemy_species],
            battle
        )
        best_enemy_move = self.damage_calculator.get_most_damaging_move(
            self.enemy_pokemon[enemy_species],
            own_pokemon_build,
            battle
        )

        print(f"Best own move: {best_own_move}")
        print(f"best enemy move: {best_enemy_move}")

        # If we can kill the enemy this move, we will
        if best_own_move[1] > enemy_hp:
            print(f"We can kill the enemy this turn!")
            if best_enemy_move[1] > own_hp:
                print(f"The enemy can kill us this turn as well!")
            else:
                print(f"Trying to kill the enemy pokemon using {best_own_move}")
                return self.create_order(Move(best_own_move[0]))

        # Switching out if we have a better option
        if own_species not in current_enemy_checks + current_enemy_counter:
            print(f"Current matchup is not favorable!")
            if len(current_enemy_checks) > 0:
                print(f"Switching to check: {current_enemy_checks[0]}")
                check = [p for p in battle.available_switches if p.species == current_enemy_checks[0]][0]
                return self.create_order(check)
            elif len(current_enemy_counter) > 0:
                print(f"Switching to counter: {current_enemy_counter[0]}")
                counter = [p for p in battle.available_switches if p.species == current_enemy_counter[0]][0]
                return self.create_order(counter)
            else:
                print(f"We don't have a better option. Trying to defeat {enemy_species} with {own_species}")

        print(f"Picking the most damaging move from {own_species} against {enemy_species}")
        return self.create_order(Move(best_own_move[0]))



    def update_enemy_information(self, battle: AbstractBattle):
        """Updates information gathered about the enemy Pokémon
        :return: True if we gathered new information, False otherwise
        """

        gathered_new_information = False

        for pokemon in battle.opponent_team:
            if battle.opponent_team[pokemon].species not in self.enemy_pokemon.keys():
                self.enemy_pokemon[battle.opponent_team[pokemon].species] = \
                    PokemonBuild(battle.opponent_team[pokemon].species,
                                 battle.opponent_team[pokemon].level,
                                 battle.opponent_team[pokemon].gender.name,
                                 battle.opponent_team[pokemon].item,
                                 battle.opponent_team[pokemon].ability)

                gathered_new_information = True

        res = self.enemy_pokemon[battle.opponent_active_pokemon.species] \
            .update_pokemon(battle.opponent_active_pokemon)

        return res or gathered_new_information


async def main():
    p1 = RuleBasedPlayer(battle_format="gen8randombattle", max_concurrent_battles=20)
    p2 = MaxDamagePlayer(battle_format="gen8randombattle")

    await p1.battle_against(p2, n_battles=20)

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Max Damage")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
