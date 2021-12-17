"""Connecting to showdown and accepting all challenges!"""
import asyncio
import os
from dotenv import load_dotenv
from poke_env.player_configuration import PlayerConfiguration
from poke_env.server_configuration import ShowdownServerConfiguration

from src.pokemon.bot.RuleBasedPlayer import RuleBasedPlayer


async def main():

    load_dotenv()

    showdown_user_name = os.getenv("SHOWDOWN_USER_NAME")
    showdown_user_password = os.getenv("SHOWDOWN_USER_PASSWORD")

    print(showdown_user_name)
    print(showdown_user_password)

    config = PlayerConfiguration(username=showdown_user_name, password=showdown_user_password)
    player = RuleBasedPlayer(
        battle_format="gen8randombattle",
        player_configuration=config,
        server_configuration=ShowdownServerConfiguration,
        save_replays=True)

    await player.accept_challenges(None, 1)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
