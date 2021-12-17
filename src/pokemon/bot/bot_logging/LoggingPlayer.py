import asyncio

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer

from src.pokemon import logger


class LoggingPlayer(Player):
    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        if battle.turn == 1:
            logger.info(f'Battle: {battle.battle_tag}')

        logger.info(f'Turn: {battle.turn}')
        logger.info(f'Pokemon:\n'
                    '\t{}'.format('\n\t'.join([p for p in battle.team])))

        logger.info("End of Turn!")
        return self.choose_random_move(battle)


async def main():
    p1 = LoggingPlayer(battle_format='gen8randombattle', save_replays="src/data/replays")
    p2 = RandomPlayer(battle_format='gen8randombattle')

    await p1.battle_against(p2, n_battles=4)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
