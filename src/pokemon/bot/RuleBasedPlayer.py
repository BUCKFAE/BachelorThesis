import asyncio
import sys
from typing import Dict, List, Optional

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
from src.pokemon.bot.matchup.field.field_state import battle_to_field
from src.pokemon.bot.matchup.one_vs_one_strategy import OneVsOneStrategy
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.pokemon.config import MATCHUP_MOVES_DEPTH
from src.pokemon.data_handling.util.pokemon_creation import build_from_pokemon


class RuleBasedPlayer(Player):
    # Stores the builds of all enemy Pokemon
    enemy_builds: Dict[str, PokemonBuild] = {}

    # Strategy on how to beat the current enemy
    current_strategy: Optional[OneVsOneStrategy] = None

    matchups: List[PokemonMatchup] = []

    # Stores the damage calculator
    damage_calculator = DamageCalculator()

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        # Logging the tag of the battle on the first turn in order to combine logs and replays
        if battle.turn == 1:

            self.enemy_builds = {}
            self.current_strategy = None
            self.matchups = []

            print(f'\n\n\n\n{self.n_won_battles} / {self.n_lost_battles}\n\n\n\n')
            logger.info(f'Battle: {battle.battle_tag}')

        alive_team = [p.species for p in battle.team.values() if not p.fainted]

        # Logging turn and remaining team
        # Both lines are required to enhance replays as we include the remaining team in the first turn in the
        # replay name and the turn id to print logs at the correct spot in the replay file
        logger.info(f'Turn {battle.turn}')
        logger.info(f'Remaining team:\n\t' + ' '.join(alive_team))

        # TODO: Determine at what point to leave early game
        # TODO: Update all matchups on switch to late game
        is_early_game = True
        logger.info(f'Early Game: {is_early_game}')

        own_species = battle.active_pokemon.species
        enemy_species = battle.opponent_active_pokemon.species

        logger.info(f'Matchup: \"{own_species}\" vs \"{enemy_species}\"')

        # Updating all matchups of which we gathered new information
        matchups_to_update = self.update_enemy_information(battle)
        self.matchups = determine_matchups(battle, self.enemy_builds, existing_matchups=self.matchups,
                                           matchups_to_update=matchups_to_update, is_early_game=is_early_game)

        # Getting all matchups involving the current enemy
        enemy_matchups = [m for m in self.matchups if m.pokemon_2.species == enemy_species]

        current_enemy_checks = []
        current_enemy_counters = []
        current_enemy_walls = []

        # Getting Walls, Checks and Counters for the current enemy
        for matchup in enemy_matchups:

            # Ensuring the matchup contains the correct pokemon
            if enemy_species != matchup.pokemon_2.species:
                logger.critical(f'Enemy species was not what we expected\n'
                                f'\tExpected: {enemy_species}\n'
                                f'\tActual: {matchup.pokemon_2.species}')

            matchup_own_species = matchup.pokemon_1.species

            # Ensuring our Pokemon is alive
            assert not _pokemon_from_species(matchup_own_species, battle).fainted

            if matchup.is_check(matchup_own_species, enemy_species):
                current_enemy_checks.append(matchup_own_species)
            if matchup.is_counter(matchup_own_species, enemy_species):
                current_enemy_counters.append(matchup_own_species)
            if matchup.is_wall(matchup_own_species, enemy_species):
                current_enemy_walls.append(matchup_own_species)

        logger.info(f'Checks: {current_enemy_checks}')
        logger.info(f'Counter: {current_enemy_counters}')
        logger.info(f'Walls: {current_enemy_walls}')

        # Switching if we have to
        if len(battle.available_moves) == 0:
            logger.info(f'We have to switch Pokemon')

            if is_early_game:
                # Removing the active Pokemon from Checks / Counters / Walls
                current_enemy_checks = [c for c in current_enemy_checks if c != own_species]
                current_enemy_counters = [c for c in current_enemy_counters if c != own_species]
                current_enemy_walls = [c for c in current_enemy_walls if c != own_species]

                # Switching to wall > check > counter
                if len(current_enemy_walls) > 0:
                    logger.info(f'\tSwitching to wall')
                    switch = current_enemy_walls[0]
                elif len(current_enemy_checks) > 0:
                    switch = current_enemy_checks[0]
                    logger.info(f'\tSwitching to check')
                elif len(current_enemy_counters) > 0:
                    logger.info(f'\tSwitching to counter')
                    switch = current_enemy_counters[0]
                else:
                    # TODO: Determine better Pokemon to switch into
                    logger.info(f'\tSwitching random')
                    switch = battle.available_switches[0].species

            else:
                # TODO: Use MinMax to determine switch in defeat phase
                switch = None

            assert switch is not None
            new_pokemon = _pokemon_from_species(switch, battle)
            logger.info(f'\tSwitching to {new_pokemon}')
            return self.create_order(new_pokemon)

        # Getting the matchup of both active Pokemon
        current_matchup = [m for m in enemy_matchups if m.pokemon_1.species == own_species]
        assert len(current_matchup) == 1
        current_matchup = current_matchup[0]

        speed_p1 = battle.active_pokemon.stats["spe"]
        speed_p2 = self.enemy_builds[enemy_species].get_most_likely_stats()["spe"]
        logger.info(f'Speed: {speed_p1} vs {speed_p2}')

        hp_p1 = battle.active_pokemon.current_hp
        hp_p2 = self.enemy_builds[enemy_species].get_remaining_hp(battle.opponent_active_pokemon.current_hp_fraction)
        logger.info(f'HP: {hp_p1} vs {hp_p2}')

        own_pokemon_build = build_from_pokemon(battle.active_pokemon)
        own_possible_moves = [m.id for m in battle.available_moves]

        # If the matchup changed we have to make a new strategy vs the opponent
        if self.current_strategy is None or \
                self.current_strategy.needs_update(own_species, enemy_species, own_possible_moves):
            optimal_moves = get_optimal_moves(
                own_pokemon_build,
                self.enemy_builds[enemy_species],
                own_possible_moves,
                MATCHUP_MOVES_DEPTH,
                damage_calculator=self.damage_calculator,
                field_state=battle_to_field(battle),
                attacker_pokemon=battle.active_pokemon,
                defender_pokemon=battle.opponent_active_pokemon,
                is_early_game=is_early_game
            )
            self.current_strategy = OneVsOneStrategy(own_species, enemy_species, optimal_moves)

        best_own_move = self.current_strategy.get_next_move()
        assert best_own_move.move in own_possible_moves
        logger.info(f'Best move of {own_species} (p1): {best_own_move}')

        best_enemy_move = current_matchup.get_optimal_moves_for_species(enemy_species)[0]
        logger.info(f'Best move of {enemy_species} (p2): {best_enemy_move}')

        # Killing the enemy if possible
        if best_own_move.get_min_damage() > hp_p2:
            # The enemy either can't kill us with his next move or is slower
            if best_enemy_move.get_max_damage() < hp_p1 or speed_p1 > speed_p2:
                logger.info(f'We can kill the enemy this turn!')
                return self.create_order(Move(best_own_move.move))

        # Healing if we can heal more than the average enemy damage
        enemy_average_damage = current_matchup.get_average_damage_per_turn(own_species)
        best_healing_move = max(own_possible_moves, key=lambda m: Move(m).heal)
        if Move(best_healing_move).heal > 0:
            health_regenerated = battle.active_pokemon.current_hp * Move(best_healing_move).heal
            hp_lost = battle.active_pokemon.max_hp - battle.active_pokemon.current_hp
            if hp_lost > health_regenerated > enemy_average_damage:
                logger.info(f'Healing using {best_healing_move}')
                return self.create_order(Move(best_healing_move))


        # Switching if we have a better option
        if own_species not in current_enemy_walls + current_enemy_checks + current_enemy_counters:
            logger.info(f'Current matchup is not favorable!')

            # Determining optimal pokemon to switch to
            switch = None
            if len(current_enemy_walls) > 0:
                logger.info(f'\tSwitching to wall')
                switch = current_enemy_walls[0]
            elif len(current_enemy_checks) > 0:
                switch = current_enemy_checks[0]
                logger.info(f'\tSwitching to check')

            # Switching if we found a better option
            if switch is not None:
                return self.create_order(_pokemon_from_species(switch, battle))

        else:
            # Dynamaxing if we are in a good matchup, know enough of the enemy team and have good hp
            if battle.can_dynamax and len(self.enemy_builds.keys()) >= 5 and battle.active_pokemon.current_hp_fraction >= 0.7:
                logger.info(f'Dynamaxing as the matchup is good!')
                return self.create_order(Move(best_own_move.move), dynamax=True)

        # Dynamaxing on the last Pokemon
        if battle.can_dynamax and len(alive_team) == 1:
            logger.info(f'Dynamaxing as we only have one Pokemon remaining!')
            return self.create_order(Move(best_own_move.move), dynamax=True)

        # Attacking the enemy
        return self.create_order(Move(best_own_move.move))

    def update_enemy_information(self, battle: AbstractBattle) -> List[str]:
        """Updates information gathered about the enemy Pokémon
        :return: A List containing the species of all enemies with new information.
        :rtype: List[str]

        - todo:: This does not collect information if the enemy switches, e.g using Volt Switch
        """
        matchups_to_update = []

        # Updating builds for all enemy pokemon
        for pokemon in battle.opponent_team:
            # Creating new build if this is the first time we see this enemy
            if battle.opponent_team[pokemon].species not in self.enemy_builds.keys():
                self.enemy_builds[battle.opponent_team[pokemon].species] = \
                    PokemonBuild(battle.opponent_team[pokemon].species,
                                 battle.opponent_team[pokemon].level,
                                 battle.opponent_team[pokemon].gender.name,
                                 battle.opponent_team[pokemon].item,
                                 battle.opponent_team[pokemon].ability)

        # Updating information about the enemy Pokemon
        self.enemy_builds[battle.opponent_active_pokemon.species].update_pokemon(battle.opponent_active_pokemon)
        matchups_to_update.append(battle.opponent_active_pokemon.species)

        return matchups_to_update


def _pokemon_from_species(species: str, battle: AbstractBattle) -> Pokemon:
    """Gets our Pokemon with the corresponding species"""
    return [p for p in battle.team.values() if p.species == species][0]


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
