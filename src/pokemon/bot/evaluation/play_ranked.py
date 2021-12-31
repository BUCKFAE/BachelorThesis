"""Connecting to showdown and accepting all challenges!"""
import asyncio
import logging
import os
import time

from dotenv import load_dotenv
from poke_env.player_configuration import PlayerConfiguration
from poke_env.server_configuration import ShowdownServerConfiguration

from src.pokemon.bot.SimpleRuleBasedPlayer import RuleBasedPlayer


async def main():
    load_dotenv()

    showdown_user_name = os.getenv("SHOWDOWN_USER_NAME")
    showdown_user_password = os.getenv("SHOWDOWN_USER_PASSWORD")
    config = PlayerConfiguration(username=showdown_user_name, password=showdown_user_password)
    player = RuleBasedPlayer(
        battle_format="gen8randombattle",
        player_configuration=config,
        server_configuration=ShowdownServerConfiguration,
        save_replays='src/data/replays',
        max_concurrent_battles=1,
        start_timer_on_battle_start=True)

    while True:

        try:
            await player.ladder(1)
        except Exception:
            logging.critical("Unable to finish game!")

        time.sleep(5)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
