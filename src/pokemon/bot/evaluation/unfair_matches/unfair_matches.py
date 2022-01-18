import asyncio
import sys
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.battle import Battle
from poke_env.environment.pokemon import Gen8Pokemon
from poke_env.player.battle_order import BattleOrder, ForfeitBattleOrder
from poke_env.player.player import Player
from singleton_decorator import singleton

from src.pokemon import logger
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.data_handling.util.pokemon_creation import build_from_pokemon, clone_pokemon


@singleton
class Collector:
    team_1: List[Gen8Pokemon] = []
    team_2: List[Gen8Pokemon] = []

    damage_calculator = DamageCalculator()

    results = {}

    def needs_information(self) -> bool:
        return len(self.team_1) != 6 or len(self.team_2) != 6

    def add_team_info(self, team: List[Gen8Pokemon]):
        if not self.team_1:
            self.team_1 = team
        elif not self.team_2:
            self.team_2 = team
        else:
            raise ValueError(f'Reccieved more than two teams')

        #logger.info(f'Recieved team: {[p.species for p in team]}')

    def evaluate_teams(self, p1_won: bool):
        assert len(self.team_1) == 6
        assert len(self.team_2) == 6

        battle = Battle('test_battle_tag', 'buckfae', None, False)

        battle._team = {p.species: p for p in self.team_1}

        battle._opponent_team = {p.species: p for p in self.team_2}

        enemy_builds = {p.species: build_from_pokemon(p) for p in self.team_2}

        #logger.warning(f'Increase depth for more accurate results!')
        matchups = determine_matchups(battle, enemy_builds, depth=1)

        #logger.info(f'Created {len(matchups)} matchups:\n\t' +
        #            '\n\t'.join([f'{m.pokemon_1.species} - {m.pokemon_2.species}' for m in matchups]))

        good_matchups = sum([sum([
            1 if m.is_counter(m.pokemon_1.species, m.pokemon_2.species)
            else 0 for m in matchups if m.pokemon_1.species == p.species])
            for p in self.team_1])

        bad_matchups = sum([sum([
            1 if m.is_counter(m.pokemon_2.species, m.pokemon_1.species)
            else 0 for m in matchups if m.pokemon_2.species == p.species])
            for p in self.team_2])

        #logger.info(f'Good Matchups: {good_matchups}')
        #logger.info(f'Good Matchups opponent: {bad_matchups}')

        difference = good_matchups - bad_matchups
        #if difference > 0:
        #    logger.info(f'Expecting Player 1 to win!')
        #elif difference == 0:
        #    logger.info(f'Equal battle!')
        #elif difference < 0:
        #    logger.info(f'Expecting Player 2 to win!')

        logger.info(f'Winner: {"Player 1" if p1_won else "Player 2"}')

        entry = self.results.get(difference, (0, 0))
        new_entry = (entry[0] + (1 if p1_won else 0), entry[1] + (1 if not p1_won else 0))
        self.results[difference] = new_entry
        #logger.info(f'{self.results=}')

        self.team_1 = []
        self.team_2 = []

    def plot_results(self):

        logger.info(f'Plotting results!')
        logger.info(self.results)
        fig, ax = plt.subplots()
        ax.bar([t for t in self.results.keys()], [t[0] + t[1] for t in self.results.values()], color='red')
        plt.xticks(np.arange(min([t for t in self.results.keys()]), max([t for t in self.results.keys()]) + 1, 1.0))
        ax.set_ylabel("Frequency", color='red')

        ax2 = ax.twinx()
        ratio_data = [(key, value[0] / (value[0] + value[1])) for (key, value) in self.results.items()]
        logger.info(f'{ratio_data=}')
        ax2.plot(*zip(*sorted(ratio_data)), color='green')
        ax2.set_ylabel("Win rate in Percent", color='green')
        plt.show()


class SendingPlayer1(Player):

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        collector = Collector()
        # Sending information to the collector if required
        if collector.needs_information():
            collector.add_team_info([clone_pokemon(p, build_from_pokemon(p)) for p in battle.team.values()])

        return self.choose_random_move(battle)


async def main():
    p1 = SendingPlayer1(battle_format="gen8randombattle",
                        max_concurrent_battles=1)

    p2 = SendingPlayer1(battle_format="gen8randombattle",
                        max_concurrent_battles=1)

    collector = Collector()

    games_won_p1 = 0

    for i in range(5_000):
        await p1.battle_against(p2, 1)

        p1_won = p1.n_won_battles == 1
        games_won_p1 += p1_won

        collector.evaluate_teams(p1_won)
        p1.reset_battles()
        p2.reset_battles()

        logger.info(f'\n\n\nPlayed: {i}\n\n\n')

    logger.info(f'{games_won_p1=}')

    collector.plot_results()

    logger.info(f'Finished!')


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
