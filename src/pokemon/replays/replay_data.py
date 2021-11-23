class ReplayData:
    # Stores the rating of all players
    player_ratings = []

    # Stores all builds of all pokemon (pokemon -> {build: count})
    pokemon_builds = {}

    # Stores how often a pokemon knew the hazard setting move
    hazards = {}
    anti_hazards = {}
    boots = 0

    hazard_vs_clear = 0
    hazard_vs_no_clear = 0
    no_hazard_vs_clear = 0
    no_hazard_vs_no_clear = 0