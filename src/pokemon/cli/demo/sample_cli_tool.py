"""Sample CLI Tool"""

import random
import time


def main():
    print("Sample client was started!")

    for current_iteration in range(random.randint(2, 4)):

        # Asking for user input
        lower = int(input("Lower bound: "))
        upper = int(input("Upper bound: "))

        assert lower <= upper

        # Random amount of outputs
        for i in range(random.randint(lower, upper)):
            print(f"\tIteration: {i}")

            # CLI Tool needs time to calculate
            time.sleep(random.random())

            # CLI Tool sometimes sends blank lines
            if random.random() < 0.3:
                print()

    print("Done!")


if __name__ == "__main__":
    main()
