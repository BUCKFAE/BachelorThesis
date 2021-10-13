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

commands = [
    '>start {"formatid":"gen7randombattle"}',
    '>player p1 {"name":"Alice"}',
    '>player p2 {"name":"Bob"}'
]


def main():
    # TODO: Improve path import

    print("Client started!")

    command = "../pokemon-showdown/pokemon-showdown simulate-battle"

    cli = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    # Executing all commands to simulate a battle
    for current_command in commands:
        print(f"Current command:\"{current_command}\"")

        output = _send_to_showdown(cli, current_command)

        print("\t{}".format('\n\t'.join([f"Line: {i} -> {output[i]}" for i in range(len(output))])))
        print("Flushed command!")

        sys.exit(0)

    # Hitting random
    for _ in range(20):
        o1 = _send_to_showdown(cli, f">p1 move {random.randint(1, 4)}")
        o2 = _send_to_showdown(cli, f">p2 move {random.randint(1, 4)}")

        print(f"{o1=}\n{o2=}")

        _print_pokemon_info(o1[2])
        _print_pokemon_info(o2[2])

        p1 = 1  # Stores ID of active pokemon
        p2 = 1

        break


def _send_to_showdown(cli: subprocess.Popen, data: str, expected_sections=1) -> List[str]:
    # TODO: Ensure data is correct

    print(f"Sending Data to showdown: {data}")
    if data is not None:
        assert "\n" not in data
        cli.stdin.write(f"{data}\n".encode())
        cli.stdin.flush()

    # output = []
    # while cli.poll() is None:
    #     res = cli.stdout.readline().decode().strip()
    #     print(f"Reccieved message from showdown: \"{res}\"")
    #     if not res:
    #         print(f"Exiting loop because res is empty")
    #         break
    #     output.append(res)

    output = []
    res = cli.stdout.readlines()

    print(f"Showdown output: {res}")

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
