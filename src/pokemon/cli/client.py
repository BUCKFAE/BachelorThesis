"""Interacts with the pokemon showdown cli tool"""

import subprocess
import os

SHOWDOWN_PATH = "C:\\Users\\schub\\Documents\\Projects\\PokemonShowdown\\pokemon-showdown"

commands = [
    '>start {"formatid":"gen7randombattle"}',
    '>player p1 {"name":"Alice"}',
    '>player p2 {"name":"Bob"}'
]

def main():
    
    # TODO: Improve path import

    print("Client started!")

    command = f"node {SHOWDOWN_PATH} simulate-battle"

    cli = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    # Executing all commands to simulate a battle
    for current_command in commands:
        print(f"Current command:\"{current_command}\"")

        cli.stdin.write(f"{current_command}\n".encode())
        cli.stdin.flush()

        output = []

        while cli.poll() is None:
            res = cli.stdout.readline().decode().strip()
            if not res:
                break
            output.append(res)

        print("\t{}".format('\n\t'.join([f"Line: {i} -> {output[i]}" for i in range(len(output))])))
        print("Flushed comand!")


if __name__ == "__main__":
    main()