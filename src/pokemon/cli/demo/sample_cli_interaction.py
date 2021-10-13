"""Demonstrates how to interact with a CLI Tool"""

import subprocess


def main():
    print("Running test communication program!")

    lower = 3
    upper = 10

    command = "python ./src/pokemon/cli/demo/sample_cli_tool.py"

    print(f"Executing command: \"{command}\"")

    cli = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    o1 = get_cli_output(cli, str(lower))
    print(o1)

    o2 = get_cli_output(cli, str(upper))
    print(o2)

    print("Done!")


def get_cli_output(cli: subprocess.Popen, data: str):
    print(f"Sending data to cli tool: {data}")

    # Sending Data to tool
    cli.stdin.write(f"{data}\n".encode())
    cli.stdin.flush()

    output = []

    # Getting all data until user input is required
    while cli.poll() is None:
        res = cli.stdout.readline().decode().strip()
        print(f"Received message from showdown: \"{res}\"")
        if not res:
            print(f"Exiting loop because res is empty")
            break
        output.append(res)

    return output


if __name__ == "__main__":
    main()
