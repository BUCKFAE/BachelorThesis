import asyncio
from typing import Dict, List

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player

from src.pokemon import logger
from src.pokemon.bot.MaxDamagePlayer import MaxDamagePlayer
from src.pokemon.bot.bot_logging.replay_enhancing import enhance_replays
from src.pokemon.bot.damage_calculator.damage_calculator import DamageCalculator
from src.pokemon.bot.damage_calculator.pokemon_build import PokemonBuild
from src.pokemon.bot.matchup.determine_matchups import determine_matchups
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup
from src.pokemon.data_handling.util.pokemon_creation import build_from_pokemon


class RuleBasedPlayer(Player):
    # Storing all information we have of the enemy Pokémon
    enemy_pokemon: Dict[str, PokemonBuild] = {}

    # Storing Matchup information
    matchups: List[PokemonMatchup] = []

    damage_calculator = DamageCalculator()

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:

        if battle.turn == 1:
            logger.info(f'Battle: {battle.battle_tag}')

        logger.info(f'Turn: {battle.turn}')

        logger.info(f'Remaining team:\n\t' +
                    ' '.join([p.species for p in battle.team.values() if not p.fainted]))

        logger.info(f"Matchup: {battle.active_pokemon.species} vs {battle.opponent_active_pokemon.species}")

        own_species = battle.active_pokemon.species
        enemy_species = battle.opponent_active_pokemon.species

        # Updating information we gathered about the enemy team
        new_information_collected = self.update_enemy_information(battle)

        #logger.info(f"Items:\n"
        #            f"\tOwn Item: {battle.active_pokemon.item}\n"
        #            f"\tEnemy Item: {self.enemy_pokemon[enemy_species].get_most_likely_item()}")

        # Determining matchup again if new information was gathered
        if new_information_collected or battle.active_pokemon.first_turn:
            logger.info(f'Gathered new Information, determining matchups.')
            # Getting current Matchup
            self.matchups = determine_matchups(battle, self.enemy_pokemon)
            #logger.info(f'Checks / Counter: {self.matchups}')

        enemy_matchups = self._find_matchups_pokemon(enemy_species)

        # Player switched to an unknown Pokémon within the turn, e.g. Voltswitch
        if len(enemy_matchups) == 0:
            logger.info("Enemy pokemon unknown, getting matchups")
            self.matchups = determine_matchups(battle, self.enemy_pokemon)
            enemy_matchups = self._find_matchups_pokemon(enemy_species)

        # Checking if our current matchup is bad
        # TODO: This is really janky, but i wrote it deep in the night because i wanted to finish the new bot
        current_enemy_checks = [matchup for matchup in enemy_matchups if
                                matchup.pokemon_1 in (battle.available_switches + [battle.active_pokemon])
                                and matchup.is_check(matchup.pokemon_1.species, enemy_species)]
        current_enemy_counter = [matchup for matchup in enemy_matchups if
                                 matchup.pokemon_1 in (battle.available_switches + [battle.active_pokemon])
                                 and matchup.is_counter(matchup.pokemon_1.species, enemy_species)]

        logger.info(f'Checks : {" ".join([c.pokemon_1.species for c in current_enemy_checks])}')
        logger.info(f'Counter: {" ".join([c.pokemon_1.species for c in current_enemy_counter])}')

        # Switching if we have to
        if not battle.available_moves:
            # print(f"Forced to switch!")
            current_enemy_checks = [c for c in current_enemy_checks if c != own_species]
            current_enemy_counter = [c for c in current_enemy_counter if c != own_species]

            if len(current_enemy_checks) > 0:
                logger.info(f"\t\tSwitching to check: {current_enemy_checks[0].pokemon_1.species}")
                check = current_enemy_checks[0].pokemon_1
                return self.create_order(check)
            elif len(current_enemy_counter) > 0:
                logger.info(f"\t\tSwitching to counter: {current_enemy_counter[0]}")
                counter = current_enemy_counter[0].pokemon_1
                return self.create_order(counter)
            else:
                return self.choose_random_move(battle)

        # Getting HP
        own_hp = battle.active_pokemon.current_hp
        enemy_hp = self.enemy_pokemon[enemy_species].get_remaining_hp(
            battle.opponent_active_pokemon.current_hp_fraction)

        # Testing if we can kill the opponent this turn
        # print(f"HP: {own_hp} - {enemy_hp}")

        # Getting Speed
        own_speed = battle.active_pokemon.stats["spe"]
        enemy_speed = self.enemy_pokemon[enemy_species].get_most_likely_stats()["spe"]
        logger.info(f"Speed: {own_speed} - {enemy_speed}")

        # TODO: Better to account for usable moves here
        own_pokemon_build = build_from_pokemon(battle.active_pokemon)
        own_pokemon_build._possible_builds[0][0]["moves"] = \
            "|".join([m for m in own_pokemon_build._possible_builds[0][0]["moves"].split("|") if m in
                      [m.id for m in battle.available_moves]])

        # Getting the most damaging moves
        # TODO: This is really janky as well
        best_own_move = [m.get_optimal_moves_for_species(own_species) for m
                         in self._find_matchups_pokemon(enemy_species) if m.pokemon_1.species == own_species][0][0]

        best_enemy_move = [m.get_optimal_moves_for_species(enemy_species) for m
                           in self._find_matchups_pokemon(enemy_species) if m.pokemon_1.species == own_species][0][0]

        logger.info(f"Best own move: {best_own_move}")
        logger.info(f"Best enemy move: {best_enemy_move}")

        # If we can kill the enemy this move, we will
        if best_own_move.get_average_damage() > enemy_hp:
            logger.info(f"\tWe can kill the enemy this turn!")
            if best_enemy_move.get_average_damage() > own_hp:
                logger.info(f"\tThe enemy can kill us this turn as well!")
                pass
            else:
                logger.info(f"\tTrying to kill the enemy pokemon using {best_own_move}")
                return self.create_order(Move(best_own_move.move))

        # Switching out if we have a better option
        if False:
        #if own_species not in current_enemy_checks + current_enemy_counter and not battle.active_pokemon.is_dynamaxed:
            logger.info(f"\tCurrent matchup is not favorable!")
            if len(current_enemy_checks) > 0:
                logger.info(f"\t\tSwitching to check: {current_enemy_checks[0].pokemon_1.species}")
                check = current_enemy_checks[0].pokemon_1
                return self.create_order(check)
            elif len(current_enemy_counter) > 0:
                logger.info(f"\t\tSwitching to counter: {current_enemy_counter[0]}")
                counter = current_enemy_counter[0].pokemon_1
                return self.create_order(counter)
            else:
                logger.info(f"\t\tWe don't have a better option. Trying to defeat {enemy_species} with {own_species}")
                pass
        else:
            if len(battle.opponent_team) > 4 and battle.can_dynamax:
                return self.create_order(Move(best_own_move.move), dynamax=True)

        if best_own_move.move not in [m.id for m in battle.available_moves]:
            logger.critical('AHSHSDHKFLSDHFLSHDFLSHDF')
            return self.choose_random_move(battle)

        logger.info(f"Picking the most damaging move from {own_species} against {enemy_species}")
        return self.create_order(Move(best_own_move.move))

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

    def _find_matchups_pokemon(self, species: str) -> list[PokemonMatchup]:
        """Returns the Matchup for the given Pokemon"""
        return [m for m in self.matchups if m.pokemon_1.species == species or m.pokemon_2.species == species]


async def main():
    p1 = RuleBasedPlayer(battle_format="gen8randombattle",
                         max_concurrent_battles=1,
                         save_replays='src/data/replays',
                         start_timer_on_battle_start=True)
    p2 = MaxDamagePlayer(battle_format="gen8randombattle")

    await p1.battle_against(p2, n_battles=1)

    print(f"RuleBased ({p1.n_won_battles} / {p2.n_won_battles}) Max Damage")

    #print(f"Enhancing Replays")
    #enhance_replays()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
