"""Sample CLI Tool"""

import random

def main():

    print("Sample client was started!")

    lower = int(input("Lower bound: "))
    upper = int(input("Upper bound: "))

    assert lower <= upper

    for i in range(random.randint(lower, upper)):
        print(f"Iteration: {i}")

    print("Done!")

if __name__ == "__main__":
    main()