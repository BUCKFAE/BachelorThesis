"""Interacts with the pokemon showdown cli tool"""
import re
import subprocess
import os
import json
import sys
import time
import random

from typing import List

# TODO: Improve path input
SHOWDOWN_PATH = "../pokemon-showdown/pokemon-showdown"

# Second entry in the tuple: How many empty lines until all output is reccieved
commands = [
    ('>start {"formatid":"gen7randombattle"}', 1),
    ('>player p1 {"name":"Alice"}', 1),
    ('>player p2 {"name":"Bob"}', 3)
]


def main():
    # TODO: Improve path import

    print("Client started!")

    command = "../pokemon-showdown/pokemon-showdown simulate-battle"

    cli = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    output = []

    # Executing all commands to simulate a battle
    for command in commands:
        current_command = command[0]
        blank_line_count = command[1]

        print(f"Current command:\"{current_command}\" ({blank_line_count})")

        output = _send_to_showdown(cli, current_command, blank_line_count)

        print("\t{}".format('\n\t'.join([f"{i} -> {output[i]}" for i in range(len(output))])))
        print("Flushed command!")

    # Stores the id of the active pokemon, pokemon indices start at 1
    active_pokemon_p1 = 1
    active_pokemon_p2 = 1

    # Keeps track what pokemon are still alive
    # TODO: Track other stats (HP / PP / STATUS)
    alive_pokemon_p1 = [True] * 6
    alive_pokemon_p2 = [True] * 6

    # Keeps track what moves are still available
    # TODO: Store PP
    moves_pp_count_p1 = _extract_viable_moves(output[2])
    moves_pp_count_p2 = _extract_viable_moves(output[6])

    print("\n\nSuccessfully initialized battle, now, fight!\n\n")

    print(f"PP left P1: {moves_pp_count_p1}")
    print(f"PP left P2: {moves_pp_count_p2}")

    # Hitting random
    while True:

        # Selecting a random valid move for each player
        move_p1 = random.choice([i + 1 for i in range(4) if moves_pp_count_p1[i]])
        move_p2 = random.choice([i + 1 for i in range(4) if moves_pp_count_p2[i]])

        o1 = _send_to_showdown(cli, f">p1 move {move_p1}", 0)
        battle_result = _send_to_showdown(cli, f">p2 move {move_p2}", 3)

        print("BattleResult:\n" + "\n\t".join(battle_result))

        if o1[0]:
            print(f"{o1=}")
            sys.exit(1)

        if not any(["error" in res for res in battle_result]):
            # If no error occurs, we print the output

            # Printing info starting at the first move
            battle_result_formatted = "\n\t".join(battle_result)
            print(f"\n\nBattle result:\n{battle_result_formatted}\n\n")

            # Printing team info for both players
            _print_pokemon_info(battle_result[2])
            _print_pokemon_info(battle_result[6])

            p1_switch = False
            p2_switch = False

            # Checking if a pokemon died
            if any(["|faint|" in a for a in battle_result]):
                print("A pokemon fainted!")

                faint_strings = [a for a in battle_result if "|faint|" in a]
                p1_switch = any(["p1" in p for p in faint_strings])
                p2_switch = any(["p2" in p for p in faint_strings])

                if p1_switch:
                    alive_pokemon_p1[active_pokemon_p1 - 1] = False

                if p2_switch:
                    alive_pokemon_p2[active_pokemon_p2 - 1] = False

            # If a player waits, the other player has to switch his pokemon
            if any(["forceSwitch\":[true]" in a for a in battle_result]):
                wait_strings = [a for a in battle_result if "forceSwitch\":[true]" in a]
                p1_switch = any(["p1" in p for p in wait_strings]) or p1_switch
                p2_switch = any(["p2" in p for p in wait_strings]) or p2_switch

            if not all(alive_pokemon_p1) or not all(alive_pokemon_p2):
                print(battle_result)

            # TODO: Program breaks if both players have to switch

            if p1_switch:
                print("The pokemon of Player 1 fainted!")
                active_pokemon_p1 = alive_pokemon_p1.index(True) + 1
                print(f"New active Pokemon P1: {active_pokemon_p1}")
                switch_output = _send_to_showdown(cli, f">p1 switch {active_pokemon_p1}", 3 if not p2_switch else 0)
                print("Output from switching:")
                print("\n\t".join(switch_output))

            if p2_switch:
                print("The pokemon of Player 2 fainted!")
                active_pokemon_p2 = alive_pokemon_p2.index(True) + 1
                print(f"New active Pokemon P2: {active_pokemon_p2}")
                switch_output = _send_to_showdown(cli, f">p2 switch {active_pokemon_p2}", 3)
                print("Output from switching:")
                print("\n\t".join(switch_output))

            if not p1_switch and not p2_switch:
                moves_pp_count_p1 = _extract_viable_moves(battle_result[2])
                moves_pp_count_p2 = _extract_viable_moves(battle_result[6])

                print(f"PP left P1: {moves_pp_count_p1}")
                print(f"PP left P2: {moves_pp_count_p2}")

        else:
            # An error occurred
            battle_result_formatted = "\n\t".join(battle_result)
            print(f"\n\nBattle result:\n{battle_result_formatted}\n\n")

            print("\n\nERROR\n\n")
            sys.exit(1)

def _extract_viable_moves(info: str) -> List[int]:
    moves = re.sub("\\|request\\|{\"active\":\\[", "", info)

    print("Formatted")
    print(moves)

    moves = moves.split("],\"side\"")[0]
    # print(f"Moves:\n{moves}")
    try:
        moves_loaded = json.loads(moves)
    except Exception:
        print("Unable to extract moves!")
        print(info)
        sys.exit(1)
    # print(json.dumps(moves_loaded, indent=4))

    if moves_loaded["moves"][0]["move"] == "Struggle":
        return [1] * 4

    # TODO: Not detecting trapped properly yet
    if "trapped:" in info:
        print("Pokemon is trapped!")
        return [1] + [0] * 3

    available = [move["pp"] if not move["disabled"] else 0 for move in moves_loaded["moves"]]
    return available


def _send_to_showdown(cli: subprocess.Popen, data: str, expected_sections=1) -> List[str]:
    # TODO: Write Docstring
    # TODO: Ensure data is correct

    print(f"Sending Data to showdown: {data}")
    if data is not None:
        assert "\n" not in data
        cli.stdin.write(f"{data}\n".encode())
        cli.stdin.flush()

    # No answer from showdown expected
    if expected_sections == 0:
        return [""]

    # Keeps track how many blank lines we have encountered
    blank_counter = 0

    start_time = time.time()

    output = []
    while cli.poll() is None:

        res = cli.stdout.readline().decode().strip()
        # print(f"Received message from showdown: \"{res}\"")
        if not res:
            blank_counter += 1
            if blank_counter == expected_sections:
                break

        output.append(res)

        # We made an invalid choice -> We return the output
        if "error" in res:
            print("An error has occurred! Returning output!")
            break

        # Stopping if we got no response from showdown after 5 seconds
        if time.time() - start_time >= 5:
            print("No response from showdown!")
            print("Entire Showdown log:")
            print("\n\t".join(output))

            raise Exception("No response from showdown!")

    return output


def _print_pokemon_info(info: str) -> None:
    request_part = json.loads(info.removeprefix("|request|"))

    # Getting info strings for all pokemon
    pokemon_info_strings = []
    for pokemon in request_part["side"]["pokemon"]:
        pokemon_info_strings.append(_load_pokemon_info_string_from_dict(pokemon))

    print("Team: ")
    print("\n".join(pokemon_info_strings))


def _load_pokemon_info_string_from_dict(pokemon: dict) -> str:
    # TODO: Properly extract species / gender / other relevant info
    details = pokemon.get("details")
    hp = pokemon["condition"]
    is_active = pokemon["active"]
    moves = " - ".join(pokemon["moves"])
    return f"\t{details} ({hp}) Active: {is_active}\n\t\t{moves}"


if __name__ == "__main__":
    main()

    # sample_team = json.load(open("src/pokemon/cli/sample.json"))

    # _extract_pokemon_from_dict(sample_team)

    # Parsing Team info
    # sample_team = ''.join(open("src/pokemon/cli/sampleTeamInfo.txt", "r").readlines())
    # print(f"Sample team:\n{sample_team}")
    # _print_pokemon_info(sample_team)
