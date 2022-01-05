"""Defines current configuration"""

import os

import dotenv

dotenv.load_dotenv()

# Path where generated builds will be stored
GENERATED_DATA_PATH = os.getenv("GENERATED_DATA_PATH")

# Path to the damage calculator node application
NODE_DAMAGE_CALCULATOR_PATH = os.getenv("NODE_DAMAGE_CALCULATOR_PATH")

# How many turns to look ahead
MATCHUP_MOVES_DEPTH = 3
