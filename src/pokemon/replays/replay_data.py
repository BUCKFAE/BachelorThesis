class ReplayData:
    # Stores the rating of all players
    player_ratings = []

    # Stores all builds of all pokemon (pokemon -> {build: count})
    pokemon_builds = {}

    # Stores how often a pokemon knew the hazard setting move
    hazards = {}
    anti_hazards = {}
    boots = 0

    