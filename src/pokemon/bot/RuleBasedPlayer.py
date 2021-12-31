import asyncio
from typing import Dict, List

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player

from src.pokemon import logger
from src.pokemon.bot.MaxDamagePlayer import MaxDamagePlayer
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.determine_matchups import determine_matchups, get_optimal_moves
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.pokemon.config import MATCHUP_MOVES_DEPTH
from src.pokemon.data_handling.util.pokemon_creation import build_from_pokemon


class RuleBasedPlayer(Player):

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        return self.choose_random_move(battle)

async def main():
    p1 = RuleBasedPlayer(battle_format="gen8randombattle",
                         max_concurrent_battles=1,
                         save_replays='src/data/replays',
                         start_timer_on_battle_start=True)
    p2 = MaxDamagePlayer(battle_format="gen8randombattle")

    await p1.battle_against(p2, n_battles=10)

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Max Damage")



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
