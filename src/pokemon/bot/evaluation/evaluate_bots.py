import asyncio
from itertools import combinations

from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer

from src.pokemon.bot.RuleBasedPlayer import RuleBasedPlayer

EVAL_EPISODES = 2


async def main():
    print("Evaluating Bots!")

    concurrent = 1

    player_list = [
        RuleBasedPlayer(battle_format="gen8randombattle", max_concurrent_battles=concurrent, save_replays=True),
        # SimpleRuleBasedPlayer(battle_format="gen8randombattle", max_concurrent_battles=concurrent),
        # MaxDamagePlayer(battle_format="gen8randombattle", max_concurrent_battles=concurrent),
        RandomPlayer(battle_format="gen8randombattle", max_concurrent_battles=concurrent),
    ]

    # Making the bots play against each other
    for battle in combinations(player_list, 2):
        p1: Player = battle[0]
        p2: Player = battle[1]
        p1_name = p1.username.split()[0]
        p2_name = p2.username.split()[0]

        p1.reset_battles()
        p2.reset_battles()

        await p1.battle_against(p2, n_battles=EVAL_EPISODES)
        print(f"{p1_name} ({p1.n_won_battles} / {p2.n_won_battles}) {p2_name}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
