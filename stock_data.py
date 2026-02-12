"""Data storage for filament stock levels.

This module defines the inventory of filament spools available in the 3D
printing farm. The data is organised by filament type (e.g. PLA Basic,
PLA Matte) and then by colour. Each entry maps a colour to the number of
full spools currently in stock. If you need to add more filament types
or colours, modify the STOCK dictionary accordingly.

Attributes:
    STOCK (dict[str, dict[str, int]]): Nested mapping of filament types to
        colours and their respective quantities.

Functions:
    get_stock() -> dict[str, dict[str, int]]: Return a deep copy of the
        STOCK dictionary. This prevents accidental modification of the
        original data when the returned object is mutated.
"""

from copy import deepcopy
from typing import Dict

# Nested dictionary representing the filament inventory. The outer keys
# correspond to the filament type, and the inner keys map colour names
# to the number of spools available. Quantities reflect full spools.
STOCK: Dict[str, Dict[str, int]] = {
    "PLA Basic": {
        "Mint Lime": 10,
        "Indigo Purple": 20,
        "Beige": 20,
        "Hot Pink": 20,
        "Blueberry Bubblegum": 10,
        "Cotton Candy Cloud": 10,
        "Arctic Whisper": 10,
        "Бронзовый": 20,
    },
    "PLA Matte": {
        "Desert Tan": 20,
        "Caramel": 20,
        "Тёмно‑синий": 20,
        "Mandarin Orange": 20,
        "Тёмно‑красный": 20,
        "Dark Chocolate": 20,
        "Ash серый": 20,
        "Ivory белый": 20,
        "Тёмно‑зелёный": 20,
    },
    "PLA Galaxy": {
        "A15-B0": 10,
        "A15-G0": 10,
        "A15-R0": 10,
        "A15-G1": 10,
    },
    "PLA Metal": {
        "Iridium": 10,
        "Iron": 10,
        "Oxide": 10,
    },
    "PLA Silk": {
        "Velvet Eclipse": 10,
        "Gilded Rose": 10,
    },
    "PLA Silk+": {
        "Белый": 10,
        "Pink": 10,
        "Baby синий": 10,
    },
    "PLA Translucent": {
        "Cherry Pink": 10,
        "Ice Blue": 10,
        "Lavender": 10,
        "Light Jade": 10,
        "Mellow Yellow": 10,
    },
}

def get_stock() -> Dict[str, Dict[str, int]]:
    """Return a copy of the current filament stock.

    Returns:
        dict[str, dict[str, int]]: A deep copy of the STOCK dictionary to
            prevent callers from mutating the original data structure.
    """
    return deepcopy(STOCK)
