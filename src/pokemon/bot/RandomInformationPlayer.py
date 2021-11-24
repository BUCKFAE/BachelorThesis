"""Random Player that prints all information to the command line"""
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.player.player import Player


class RandomInformationPlayer(Player):
    def choose_move(self, battle: AbstractBattle):
        print(battle.active_pokemon)
        return self.choose_random_move(battle)
