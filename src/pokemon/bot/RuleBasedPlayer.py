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


def _pokemon_from_species(species: str, battle: AbstractBattle) -> Pokemon:
    return [p for p in battle.team.values() if p.species == species][0]


class RuleBasedPlayer(Player):
    # Storing all information we have of the enemy Pokémon
    enemy_pokemon: Dict[str, PokemonBuild] = {}

    # Storing Matchup information
    matchups: List[PokemonMatchup] = []

    # Stores Information on how we wanna beat the enemy
    current_game_plan = ([], '', '')

    damage_calculator = DamageCalculator()

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        if battle.turn == 1:
            print(f'\n\n\n\n{self.n_won_battles} / {self.n_lost_battles}\n\n\n\n')
            logger.info(f'Battle: {battle.battle_tag}')

        # Logging info, these two are required as enhance_battles use them to determine when a new move started
        logger.info(f'Turn: {battle.turn}')
        logger.info(f'Remaining team:\n\t' + ' '.join([p.species for p in battle.team.values() if not p.fainted]))

        # Prints the current matchup
        logger.info(f"Matchup: {battle.active_pokemon.species} vs {battle.opponent_active_pokemon.species}")

        own_species = battle.active_pokemon.species
        enemy_species = battle.opponent_active_pokemon.species

        # Updating information we gathered about the enemy team
        new_information_collected = self.update_enemy_information(battle)
        # TODO: Reconsider when to update matchups
        new_information_collected = True

        # Determining matchup again if new information was gathered
        if new_information_collected or battle.active_pokemon.first_turn:
            logger.info(f'Gathered new Information, determining matchups.')
            self.matchups = determine_matchups(battle, self.enemy_pokemon, is_early_game=True)

        # Getting matchups against the current enemy
        enemy_matchups = self._find_matchups_pokemon(enemy_species)

        # Checking if our current matchup is bad
        current_enemy_checks = []
        current_enemy_counter = []

        # Determining check and counter
        for matchup in enemy_matchups:
            own_species = matchup.pokemon_1.species

            # Pokemon_1 is always our Pokemon
            assert own_species in [p.species for p in battle.team.values()]
            # Pokemon_2 is always the enemy Pokémon
            assert enemy_species == matchup.pokemon_2.species

            if matchup.is_check(own_species, enemy_species):
                current_enemy_checks.append(own_species)
            if matchup.is_counter(own_species, enemy_species):
                current_enemy_counter.append(own_species)

        # Can not always switch to every Pokemon
        allowed_switches_counter = [p for p in current_enemy_checks if [s.species for s in battle.available_switches]
                                    and battle.active_pokemon.species != p]
        allowed_switches_check = [p for p in current_enemy_checks if [s.species for s in battle.available_switches]
                                  and battle.active_pokemon.species != p]

        logger.info(f'Allowed switches counter: {allowed_switches_counter}')
        logger.info(f'Allowed switches check: {allowed_switches_check}')

        # Switching if we have to
        if len(battle.available_moves) == 0:
            logger.info('We have to switch pokemon!')
            if len(allowed_switches_check) > 0:
                switch = _pokemon_from_species(allowed_switches_check[0], battle)
            elif len(allowed_switches_counter) > 0:
                switch = _pokemon_from_species(allowed_switches_counter[0], battle)
            else:
                # Random switch
                if len(battle.available_switches) > 0:
                    switch = battle.available_switches[0]
                else:
                    logger.critical(f'Reached invalid state. Could neither move nor switch')
                    return self.choose_random_move(battle)
            logger.info(f'Switching to {switch.species}')
            return self.create_order(switch)

        # Getting HP
        own_hp = battle.active_pokemon.current_hp
        enemy_hp = self.enemy_pokemon[enemy_species].get_remaining_hp(
            battle.opponent_active_pokemon.current_hp_fraction)

        # Testing if we can kill the opponent this turn
        logger.info(f'HP: {own_hp} vs. {enemy_hp}')

        # Getting Speed
        own_speed = battle.active_pokemon.stats["spe"]
        enemy_speed = self.enemy_pokemon[enemy_species].get_most_likely_stats()["spe"]
        logger.info(f"Speed: {own_speed} vs. {enemy_speed}")

        # TODO: Better to account for usable moves here
        own_pokemon_build = build_from_pokemon(battle.active_pokemon)
        own_pokemon_build._possible_builds[0][0]["moves"] = \
            "|".join([m for m in own_pokemon_build._possible_builds[0][0]["moves"].split("|") if m in
                      [m.id for m in battle.available_moves]])

        # Getting the most damaging moves
        if not self.current_game_plan[0] or not self.current_game_plan[1] \
                or self.current_game_plan[1] != enemy_species or \
                len(self.current_game_plan[0]) == 0 or \
                self.current_game_plan[2] != own_species:
            optimal_moves = get_optimal_moves(
                own_pokemon_build,
                self.enemy_pokemon[enemy_species],
                [m.id for m in battle.available_moves],
                MATCHUP_MOVES_DEPTH,
                damage_calculator=DamageCalculator(),
                is_early_game=True
            )
            self.current_game_plan = (optimal_moves, enemy_species, own_species)

        logger.info(f'Optimal moves: {[(m.move + " " + str(m.get_average_damage()))for m in self.current_game_plan[0]]}')

        next_own_move = self.current_game_plan[0][0]
        self.current_game_plan = (self.current_game_plan[0][1:], self.current_game_plan[1], own_species)

        best_enemy_move = [m.get_optimal_moves_for_species(enemy_species) for m
                           in self._find_matchups_pokemon(enemy_species) if m.pokemon_1.species == own_species][0][0]

        # If we can kill the enemy this move, we will
        if next_own_move.get_average_damage() > enemy_hp \
                and next_own_move.move in [m.id for m in battle.available_moves]:
            logger.info(f"\tWe can kill the enemy this turn!")
            if best_enemy_move.get_min_damage() > own_hp and enemy_speed > own_speed:
                logger.info(f"\tThe enemy can kill us this turn as well!")
                if len(current_enemy_checks) > 1:
                    switch = _pokemon_from_species(allowed_switches_check[0], battle)
                    logger.info(f'Switching to check {switch.species} to save {own_species}')
                    return self.create_order(switch)
            else:
                logger.info(f"\tTrying to kill the enemy pokemon using {next_own_move.move}")
                return self.create_order(Move(next_own_move.move))

        # Switching out if we have a better option
        if own_species not in current_enemy_checks + current_enemy_counter and not battle.active_pokemon.is_dynamaxed:
            logger.info(f'Current Matchup is not favorable!')
            switch = None
            if len(allowed_switches_check) > 0:
                switch = _pokemon_from_species(allowed_switches_check[0], battle)
            elif len(allowed_switches_counter) > 0:
                switch = _pokemon_from_species(allowed_switches_counter[0], battle)

            if switch is not None:
                logger.info(f'Switching to {switch.species}')
                return self.create_order(switch)
        else:
            if len(battle.opponent_team) > 4 and battle.can_dynamax:
                return self.create_order(Move(next_own_move.move), dynamax=True)

        # TODO: fix this
        if next_own_move.move not in [m.id for m in battle.available_moves]:
            logger.critical('Best move is not available')
            return self.choose_random_move(battle)

        logger.info(f"Picking the most damaging move from {own_species} against {enemy_species}")
        logger.info(f'Own move: {next_own_move.move}: {next_own_move.get_average_damage()}')
        logger.info(f'Enemy move: {best_enemy_move.move}: {best_enemy_move.get_average_damage()}')
        return self.create_order(Move(next_own_move.move))

    def update_enemy_information(self, battle: AbstractBattle):
        """Updates information gathered about the enemy Pokémon
        :return: True if we gathered new information, False otherwise
        """

        gathered_new_information = False

        for pokemon in battle.opponent_team:
            if battle.opponent_team[pokemon].species not in self.enemy_pokemon.keys():
                self.enemy_pokemon[battle.opponent_team[pokemon].species] = \
                    PokemonBuild(battle.opponent_team[pokemon].species,
                                 battle.opponent_team[pokemon].level,
                                 battle.opponent_team[pokemon].gender.name,
                                 battle.opponent_team[pokemon].item,
                                 battle.opponent_team[pokemon].ability)

                gathered_new_information = True

        logger.info(f"Updating information about {battle.opponent_active_pokemon.species}")

        res = self.enemy_pokemon[battle.opponent_active_pokemon.species] \
            .update_pokemon(battle.opponent_active_pokemon)

        return res or gathered_new_information

    def _find_matchups_pokemon(self, species: str) -> List[PokemonMatchup]:
        """Returns the Matchup for the given Pokemon"""
        return [m for m in self.matchups if m.pokemon_1.species == species or m.pokemon_2.species == species]


async def main():
    p1 = RuleBasedPlayer(battle_format="gen8randombattle",
                         max_concurrent_battles=1,
                         save_replays='src/data/replays',
                         start_timer_on_battle_start=True)
    p2 = MaxDamagePlayer(battle_format="gen8randombattle")

    await p1.battle_against(p2, n_battles=10)

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Max Damage")

    # print(f"Enhancing Replays")
    # enhance_replays()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
