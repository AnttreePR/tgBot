from copy import deepcopy
from typing import Dict, Any

# Новый формат:
# DEFAULT_STOCK[type][color] = {"price": <руб/катушка>, "qty": <кол-во катушек>}
# Цены проставлены: 1791 или 1431 ₽ за катушку 1 кг.

DEFAULT_STOCK: Dict[str, Dict[str, Dict[str, Any]]] = {
    "PLA Basic": {
        "Mint Lime": {"price": 1791, "qty": 10},
        "Indigo Purple": {"price": 1431, "qty": 20},
        "Beige": {"price": 1431, "qty": 20},
        "Hot Pink": {"price": 1431, "qty": 20},
        "Blueberry Bubblegum": {"price": 1791, "qty": 10},
        "Cotton Candy Cloud": {"price": 1791, "qty": 10},
        "Arctic Whisper": {"price": 1791, "qty": 10},
        "Бронзовый": {"price": 1431, "qty": 20},
    },
    "PLA Matte": {
        "Desert Tan": {"price": 1431, "qty": 20},
        "Caramel": {"price": 1431, "qty": 20},
        "Тёмно-синий": {"price": 1431, "qty": 20},
        "Mandarin Orange": {"price": 1431, "qty": 20},
        "Тёмно-красный": {"price": 1431, "qty": 20},
        "Dark Chocolate": {"price": 1431, "qty": 20},
        "Ash серый": {"price": 1431, "qty": 20},
        "Ivory белый": {"price": 1431, "qty": 20},
        "Тёмно-зелёный": {"price": 1431, "qty": 20},
    },
    "PLA Galaxy": {
        "A15-B0": {"price": 1791, "qty": 10},
        "A15-G0": {"price": 1791, "qty": 10},
        "A15-R0": {"price": 1791, "qty": 10},
        "A15-G1": {"price": 1791, "qty": 10},
    },
    "PLA Metal": {
        "Iridium": {"price": 1791, "qty": 10},
        "Iron": {"price": 1791, "qty": 10},
        "Oxide": {"price": 1791, "qty": 10},
    },
    "PLA Silk": {
        "Velvet Eclipse": {"price": 1791, "qty": 10},
        "Gilded Rose": {"price": 1791, "qty": 10},
    },
    "PLA Silk+": {
        "Белый": {"price": 1791, "qty": 10},
        "Pink": {"price": 1791, "qty": 10},
        "Baby синий": {"price": 1791, "qty": 10},
    },
    "PLA Translucent": {
        "Cherry Pink": {"price": 1791, "qty": 10},
        "Ice Blue": {"price": 1791, "qty": 10},
        "Lavender": {"price": 1791, "qty": 10},
        "Light Jade": {"price": 1791, "qty": 10},
        "Mellow Yellow": {"price": 1791, "qty": 10},
    },
}

def get_default_stock():
    return deepcopy(DEFAULT_STOCK)
