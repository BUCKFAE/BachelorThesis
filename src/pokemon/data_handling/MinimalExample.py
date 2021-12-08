import asyncio

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.player.battle_order import BattleOrder, ForfeitBattleOrder
from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer


class MinimalExample(Player):

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        return ForfeitBattleOrder()


async def main():
    # Deleting old data dir

    p1 = MinimalExample(battle_format="gen8randombattle")
    p2 = RandomPlayer(battle_format="gen8randombattle")

    await p1.battle_against(p2, n_battles=60_000)

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Random")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
