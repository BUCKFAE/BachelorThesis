"""Interacts with the pokemon showdown cli tool"""

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

    # Executing all commands to simulate a battle
    for command in commands:
        current_command = command[0]
        blank_line_count = command[1]

        print(f"Current command:\"{current_command}\" ({blank_line_count})")

        output = _send_to_showdown(cli, current_command, blank_line_count)

        print("\t{}".format('\n\t'.join([f"Line: {i} -> {output[i]}" for i in range(len(output))])))
        print("Flushed command!")

    
    print("\n\nSuccessfully initialized battle, now, fight!\n\n")
    

    # Hitting random
    for _ in range(20):
        o1 = _send_to_showdown(cli, f">p1 move {random.randint(1, 4)}", 0)
        battle_result = _send_to_showdown(cli, f">p2 move {random.randint(1, 4)}", 3)

        print(f"{o1=}")

        # Printing info starting at the first move
        battle_result_formatted = "\n\t".join(battle_result[10:])
        print(f"\n\nBattle result:\n{battle_result_formatted}\n\n")

        # Printing team info for both players
        _print_pokemon_info(battle_result[2])
        _print_pokemon_info(battle_result[6])

        # Checking if a pokemon died
        if any(["|faint|" in a for a in battle_result]):
            print("A pokemon fainted!")


        p1 = 1  # Stores ID of active pokemon
        p2 = 1

def _send_to_showdown(cli: subprocess.Popen, data: str, expected_sections = 1) -> List[str]:
    # TODO: Write Docstring
    # TODO: Ensure data is correct

    print(f"Sending Data to showdown: {data}")
    if data is not None:
        assert "\n" not in data
        cli.stdin.write(f"{data}\n".encode())
        cli.stdin.flush()


    # No answer from showdown expected
    if expected_sections == 0: return [""]

    # Keeps track how many blank lines we have encountered
    blank_counter = 0

    start_time = time.time()

    output = []
    while cli.poll() is None:
        print(output)
        res = cli.stdout.readline().decode().strip()
        #print(f"Reccieved message from showdown: \"{res}\"")
        if not res:
            blank_counter += 1
            if blank_counter == expected_sections:
                print(output)
                break

        print(time.time() - start_time)

        # Stopping if we got no response from showdown after 5 seconds
        if time.time() - start_time >= 5:
            print("No response from showdown!")
            print("Entire Showdown log:")
            print("\n\t".join(output))

            raise Exception("No response from showdown!")

        output.append(res)

    print(output)

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
