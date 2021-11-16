"""Defines current configuration"""

import os

def get_showdown_port() -> int:
    return int(os.environ.get("SHOWDOWN_PORT"))