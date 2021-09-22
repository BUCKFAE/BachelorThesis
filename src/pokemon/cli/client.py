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
    '>player p2 {"name":"Bob"}',
    ''
]

def main():
    
    # TODO: Improve path import

    print("Client started!")

    command = f"node {SHOWDOWN_PATH} simulate-battle"

    cli = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    # Executing all commands to simulate a battle
    for current_command in commands:
        print(f"Current command:\"{current_command}\"")

        output = _send_to_showdown(cli, current_command)

        print("\t{}".format('\n\t'.join([f"Line: {i} -> {output[i]}" for i in range(len(output))])))
        print("Flushed comand!")


    # Hitting random
    for _ in range(20):
        o1 = _send_to_showdown(cli, f">p1 move {random.randint(1, 4)}")
        o2 = _send_to_showdown(cli, f">p2 move {random.randint(1, 4)}")

        print(f"\n\nOutput1: {o1}")
        print(f"\n\nOutput2: {o1}")

        p1 = 1 # Stores ID of active pokemon
        p2 = 1



def _send_to_showdown(cli: subprocess.Popen, data: str) -> List[str]:
    # TODO: Ensure data is correct

    assert "\n" not in data

    cli.stdin.write(f"{data}\n".encode())
    cli.stdin.flush()

    output = []
    while cli.poll() is None:
        res = cli.stdout.readline().decode().strip()
        if not res:
            break
        output.append(res)

    return output


def _extract_pokemon_from_dict(team: dict):
    print(f"Team: {team}")

    for pokemon_id in range(6):
        current_dict = team["side"]["pokemon"][pokemon_id]

        print(f"Current Pokemon: {current_dict['ident']}")


if __name__ == "__main__":
    main()

    #sample_team = json.load(open("src/pokemon/cli/sample.json"))

    #_extract_pokemon_from_dict(sample_team)