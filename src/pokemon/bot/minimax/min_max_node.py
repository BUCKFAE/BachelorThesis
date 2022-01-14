import copy
from typing import Dict, List

from src.pokemon import logger
from src.pokemon.bot.matchup.pokemon_matchup import PokemonMatchup


class MinMaxNode:

    def __init__(self,
                 own_species: str,
                 enemy_species: str,
                 remaining_hp_team_1: Dict[str, int],
                 remaining_hp_team_2: Dict[str, int],
                 matchups: List[PokemonMatchup],
                 current_depth: int = 0,
                 is_min_node: bool = True):

        self.own_species = own_species
        self.enemy_species = enemy_species
        self.remaining_hp_team_1 = remaining_hp_team_1
        self.remaining_hp_team_2 = remaining_hp_team_2
        self.matchups = matchups
        self.current_depth = current_depth
        self.children = {}
        self.is_min_node = is_min_node

    def evaluate_node(self):

        # Player 1 lost
        if all([p == 0 for p in self.remaining_hp_team_1.values()]):
            return -1

        # Player 2 lost
        if all([p == 0 for p in self.remaining_hp_team_2.values()]):
            return 1

        return sum([n.evaluate_node() for n in self.children.values()])

    def is_leaf(self):
        return all([p == 0 for p in self.remaining_hp_team_1.values()]) or \
               all([p == 0 for p in self.remaining_hp_team_2.values()])

    def build_tree_below_node(self):

        try:
            current_matchup: PokemonMatchup = list(filter(lambda matchup:
                                                          matchup.is_battle_between(self.own_species,
                                                                                    self.enemy_species),
                                                          self.matchups))[0]
        except:
            logger.info(f'Unkown matchup: {self.own_species} vs {self.enemy_species}')
            logger.info(f'Known matchups:\n'
                        '\n'.join([f'{m.pokemon_1} vs {m.pokemon_2.species}' for m in self.matchups]))
            return

        hp_p1 = self.remaining_hp_team_1[self.own_species]
        hp_p2 = self.remaining_hp_team_2[self.enemy_species]

        # Calculating the remaining HP if both Pokémon battle
        fainted_after_turns_p1 = current_matchup.expected_turns_until_faint(self.own_species, hp_p1)
        fainted_after_turns_p2 = current_matchup.expected_turns_until_faint(self.enemy_species, hp_p2)

        if fainted_after_turns_p1 == fainted_after_turns_p2:
            speed_1 = current_matchup._build_p1.get_most_likely_stats()["spe"]
            speed_2 = current_matchup._build_p2.get_most_likely_stats()["spe"]
            if speed_1 > speed_2:
                fainted_after_turns_p1 -= 1
            else:
                fainted_after_turns_p2 -= 1

        if fainted_after_turns_p1 < fainted_after_turns_p2:
            # logger.info(f'{self.own_species} faints before {self.enemy_species}')
            total_hp_p2 = self.remaining_hp_team_2[self.enemy_species]
            remaining_hp_p2 = total_hp_p2 - current_matchup.get_expected_damage_after_turns(self.enemy_species,
                                                                                            num_turns=fainted_after_turns_p1)
            # logger.info(f'{self.enemy_species} will have {remaining_hp_p2} remaining!')
            self.remaining_hp_team_1[self.own_species] = 0
            self.remaining_hp_team_2[self.enemy_species] = remaining_hp_p2

        if fainted_after_turns_p2 < fainted_after_turns_p1:
            # logger.info(f'{self.enemy_species} faints before {self.own_species}')
            total_hp_p1 = self.remaining_hp_team_1[self.own_species]
            remaining_hp_p1 = total_hp_p1 - current_matchup.get_expected_damage_after_turns(self.own_species,
                                                                                            num_turns=fainted_after_turns_p2)
            # logger.info(f'{self.own_species} will have {remaining_hp_p1} remaining!')
            self.remaining_hp_team_1[self.own_species] = remaining_hp_p1
            self.remaining_hp_team_2[self.enemy_species] = 0

            logger.info(f'Remaining HP Team1: {self.remaining_hp_team_1}')
            logger.info(f'Remaining HP Team2: {self.remaining_hp_team_2}')

            # We have to switch

        if self.remaining_hp_team_1[self.own_species] == 0:
            # logger.info('We have to make a move!')
            options = [p for p in self.remaining_hp_team_1.keys() \
                       if self.remaining_hp_team_1[p] is not None if self.remaining_hp_team_1[p] > 0]
            self.is_min_node = True
            self.children = {option: MinMaxNode(
                option,
                self.enemy_species,
                copy.deepcopy(self.remaining_hp_team_1),
                copy.deepcopy(self.remaining_hp_team_2),
                self.matchups,
                self.current_depth + 1) for option in options}

        elif self.remaining_hp_team_2[self.enemy_species] == 0:
            # logger.info('The enemy has to make a move!')
            # TODO: A dictionary entry was none here
            options = [p for p in self.remaining_hp_team_2.keys() \
                       if self.remaining_hp_team_2[p] is not None and self.remaining_hp_team_2[p] > 0]
            self.is_min_node = False
            self.children = {option: MinMaxNode(
                self.own_species,
                option,
                copy.deepcopy(self.remaining_hp_team_1),
                copy.deepcopy(self.remaining_hp_team_2),
                self.matchups,
                self.current_depth + 1) for option in options}

        else:
            raise ValueError('Neither Pokemon was dead')

            # logger.info(f'Possible switches: {options}')
        [n.build_tree_below_node() for n in self.children.values()]
