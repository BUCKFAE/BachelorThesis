from poke_env.player.player import Player


class SimpleRuleBasedPlayer(Player):
    def choose_move(self, battle):

        if battle.available_moves:
            # Finds the best move among available ones

            best_move = max(battle.available_moves, key=lambda move: self.calculate_damage(move, battle.active_pokemon,
                                                                                           battle.opponent_active_pokemon))

            best_move_damage = self.calculate_damage(best_move, battle.active_pokemon, battle.opponent_active_pokemon)

            best_switch = self.get_best_pokemon(battle.available_switches, battle.opponent_active_pokemon)

            if best_switch is not None:

                # print(f"\n\n{best_switch.moves}")

                best_switch_move = max(best_switch.moves,
                                       key=lambda move: self.calculate_damage(best_switch.moves[move],
                                                                              best_switch,
                                                                              battle.opponent_active_pokemon))

                best_switch_damage = self.calculate_damage(best_switch.moves[best_switch_move], best_switch,
                                                           battle.opponent_active_pokemon)

                if best_switch_damage > best_move_damage * 2:

                    pass

                else:
                    return self.create_order(best_move)

            else:
                return self.create_order(best_move)

        # If no attack is available, a random switch will be made

        best_switch = self.get_best_pokemon(battle.available_switches, battle.opponent_active_pokemon)

        # TODO: Fix this bug
        if best_switch is None:
            # print("Unable to find a pokemon to pick, doing something random!")
            # print(f"{battle.available_moves=}")
            # print(f"{battle.active_pokemon=}")
            # print(f"{battle.opponent_active_pokemon=}")
            return self.choose_random_move(battle)

        return self.create_order(best_switch)

    def calculate_damage(self, move, own_pokemon, enemy_pokemon):

        mul1 = move.type.damage_multiplier(enemy_pokemon.type_1, enemy_pokemon.type_2) if move.type != 0 else 1

        mul2 = 1.5 if own_pokemon.type_1 == move.type or own_pokemon.type_2 == move.type else 1
        acc = move.accuracy
        dmg = move.base_power * mul1 * mul2 * acc
        return dmg

    def get_best_pokemon(self, available_pokemon, enemy_pokemon):
        best_switch = (None, 0)

        for curr in available_pokemon:
            best_move = 0
            for move in curr.moves:
                dmg = self.calculate_damage(curr.moves[move], curr, enemy_pokemon)
                if dmg >= best_move:
                    best_move = dmg
            if best_move >= best_switch[1]:
                best_switch = (curr, best_move)

        if best_switch[0] is None:
            # TODO: Fix this bug
            return None

        return best_switch[0]
