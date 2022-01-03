import re

if __name__ == "__main__":
    with open('src/pokemon/data_handling/items/items_calc.txt', 'r') as f:
        lines = f.readlines()

        items = []

        for line in lines:
            match = re.search('\'([a-zA-Z0-9 ]+)\'', line)
            if match:
                items.append(match.group(1))

        print('\n'.join(items))