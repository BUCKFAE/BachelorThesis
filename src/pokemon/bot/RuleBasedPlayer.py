import asyncio

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player

from poke_env.player.random_player import RandomPlayer

from src.pokemon.bot.RandomInformationPlayer import RandomInformationPlayer
from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild


class RuleBasedPlayer(Player):
    # Storing all information we have of the enemy pokemon
    enemy_pokemon = {}



    timer = 0

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        print(f"Choosing move")

        self.update_enemy_information(battle)

        self.timer += 1
        if self.timer == 10:
            determine_matchups(battle, self.enemy_pokemon)

        return self.choose_random_move(battle)

    def update_enemy_information(self, battle: AbstractBattle):

        for pokemon in battle.opponent_team:
            if battle.opponent_team[pokemon].species not in self.enemy_pokemon.keys():

                # TODO: Fix galar / special forms

                if "ygard" in battle.opponent_team[pokemon].species:
                    print(f"\n\nZYGARDE:")
                    print(battle.opponent_team[pokemon].species)

                self.enemy_pokemon[battle.opponent_team[pokemon].species] = \
                    PokemonBuild(pokemon.split()[1],
                                 battle.opponent_team[pokemon].level,
                                 battle.opponent_team[pokemon].gender.name,
                                 battle.opponent_team[pokemon].item,
                                 battle.opponent_team[pokemon].ability)

        self.enemy_pokemon[battle.opponent_active_pokemon.species] \
            .update_pokemon(battle.opponent_active_pokemon)


async def main():
    p1 = RuleBasedPlayer(battle_format="gen8randombattle", max_concurrent_battles=1)
    p2 = RandomInformationPlayer(battle_format="gen8randombattle")

    await p1.battle_against(p2, n_battles=1)

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Random")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
