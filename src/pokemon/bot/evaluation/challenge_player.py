import asyncio
import os
import time

from dotenv import load_dotenv
from poke_env.player_configuration import PlayerConfiguration
from poke_env.server_configuration import ShowdownServerConfiguration, LocalhostServerConfiguration

from src.pokemon.bot.RuleBasedPlayer import RuleBasedPlayer


async def main():
    load_dotenv()

    showdown_user_name = os.getenv("SHOWDOWN_USER_NAME")
    showdown_user_password = os.getenv("SHOWDOWN_USER_PASSWORD")
    config = PlayerConfiguration(username=showdown_user_name, password=showdown_user_password)
    player = RuleBasedPlayer(
        battle_format="gen8randombattle",
        player_configuration=config,
        server_configuration=LocalhostServerConfiguration,
        save_replays='src/data/replays',
        max_concurrent_battles=1,
        start_timer_on_battle_start=True)

    while True:
        await player.send_challenges("HerrDonner", 1)
        time.sleep(10)

    print(f'Stats: {player.n_won_battles} / {player.n_lost_battles}')

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
