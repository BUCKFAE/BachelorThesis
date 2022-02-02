import glob
from src.pokemon import logger

def main():
    logger.info(f'Calculating amout of game states.')

    # Stores all Pokémon
    pokemon = {}

    for file_path in glob.iglob('src/data/generated/*'):
        current_pokemon = file_path.split('/')[-1].removesuffix('.txt')
        logger.info(f'Current Pokemon: {current_pokemon}')

        with open(file_path, 'r') as pokemon_file:
            pokemon_builds = pokemon_file.readlines()

            # Storing how many builds a pokemon has. Ignoring very unlikely builds
            for pokemon_build in [line for line in pokemon_builds if line.strip()]:

                occurences = int(pokemon_build.split('-')[0].strip())
                if occurences < 3:
                    logger.info(f'Ignoring build for {current_pokemon}: {occurences} occurences') 
                else: 
                    pokemon[current_pokemon] = pokemon.get(current_pokemon, 0) + 1


    # Calculation of possible starting states
    pokemon_count = len(pokemon.keys())
    logger.info(f'Pokemon: {pokemon_count}')

    average_variance_count = int(sum(pokemon.values()) / len(pokemon.values()))
    logger.info(f'Average builds per Pokémon: {average_variance_count}')

    possible_states = 1

    for team_id in range(0, 2):
        logger.info(f'Team ID: {team_id}')
        for slot_id in range(0, 6):
            possible_pokemon = pokemon_count - slot_id
            logger.info(f'Possible Pokémon in slot: {slot_id}: {possible_pokemon}')
            possible_pokemon_with_build = possible_pokemon * average_variance_count
            logger.info(f'Possible Pokémon including build in slot {slot_id}: {possible_pokemon_with_build}')

            possible_states *= possible_pokemon_with_build

        logger.info(f'Possible team combinations: {possible_states}')
        possible_states *= 6
        logger.info(f'Possible team combinations (active Pokémon): {possible_states}')


if __name__ == "__main__":
    main()