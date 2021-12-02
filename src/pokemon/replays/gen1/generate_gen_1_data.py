"""Used to generate all possible gen 1 builds
# TODO
"""
import asyncio

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer

from src.pokemon.replays.util import convert_species_to_file_name

PATH = "src/pokemon/replays/data"


class DumpingPlayer(Player):

    def __init__(self, battle_format):
        super().__init__(battle_format=battle_format)
        self.is_first_move = True

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        if self.is_first_move:
            # Gathering all information of our team
            print("First move!")
            self.is_first_move = False

            #for pokemon in battle.team:
                #name = convert_species_to_file_name(pokemon)
                #print(f"Pokemon: {pokemon} -> {name}")

        return self.choose_random_move(battle)


async def main():
    p1 = DumpingPlayer(battle_format="gen1randombattle")
    p2 = RandomPlayer(battle_format="gen1randombattle")

    await p1.battle_against(p2, n_battles=100)

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Random")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
