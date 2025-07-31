# utils/sector_map.py

import json
import os

# Support loading whether run from root or inside a subfolder
SECTOR_FILE = "symbol_sector.json"

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir,SECTOR_FILE)

if os.path.exists(file_path):
    with open(file_path, "r") as f:
        sector_map = json.load(f)


def get_sector(symbol):
    """
    Returns the sector for a given symbol string.
    If not found, returns 'Unknown'.
    """
    return sector_map.get(symbol.upper(), "Unknown")
