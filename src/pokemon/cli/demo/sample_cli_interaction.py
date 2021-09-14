"""Demonstrates how to interact with a CLI Tool"""

import subprocess
import time
import os

def main():

    print("Running test communication program!")

    lower = 3
    upper = 10

    command = "python .\\src\\pokemon\\cli\\demo\\sample_cli_tool.py"

    print(f"Executing command: \"{command}\"")

    res = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    cli_output = res.stdout.readline().decode()
    print(f"{cli_output=}")

    res.stdin.write(f"{lower}\n".encode())
    res.stdin.write(f"{upper}\n".encode())
    res.stdin.flush()

    cli_output = "".join([i.decode() for i in res.stdout.readlines()])

    print(cli_output)

    print("Done!")






if __name__ == "__main__":
    main()