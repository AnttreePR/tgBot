import json
import os
from copy import deepcopy
from typing import Dict, Any, Tuple

STOCK_FILE = os.path.join(os.path.dirname(__file__), "stock.json")


def load_stock(default_stock: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    if not os.path.exists(STOCK_FILE):
        save_stock(default_stock)
        return deepcopy(default_stock)

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    stock: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for t, colors in data.items():
        stock[t] = {}
        for c, meta in colors.items():
            price = float(meta.get("price", 0))
            qty = int(meta.get("qty", 0))
            stock[t][c] = {"price": price, "qty": qty}
    return stock


def save_stock(stock: Dict[str, Dict[str, Dict[str, Any]]]) -> None:
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(stock, f, ensure_ascii=False, indent=2)


def exists_plastic(stock: Dict[str, Dict[str, Dict[str, Any]]], ptype: str, color: str) -> bool:
    return ptype in stock and color in stock[ptype]


def add_or_update_plastic(
    stock: Dict[str, Dict[str, Dict[str, Any]]],
    ptype: str,
    color: str,
    price_per_spool: float,
    qty: int,
) -> None:
    stock.setdefault(ptype, {})
    stock[ptype][color] = {"price": float(price_per_spool), "qty": int(qty)}


def delete_plastic(stock: Dict[str, Dict[str, Dict[str, Any]]], ptype: str, color: str) -> bool:
    if ptype not in stock or color not in stock[ptype]:
        return False
    del stock[ptype][color]
    if not stock[ptype]:
        del stock[ptype]
    return True


def change_qty(stock: Dict[str, Dict[str, Dict[str, Any]]], ptype: str, color: str, delta: int) -> Tuple[bool, int]:
    if not exists_plastic(stock, ptype, color):
        return False, 0
    new_qty = max(0, int(stock[ptype][color]["qty"]) + int(delta))
    stock[ptype][color]["qty"] = new_qty
    return True, new_qty


def set_price(stock: Dict[str, Dict[str, Dict[str, Any]]], ptype: str, color: str, price: float) -> bool:
    if not exists_plastic(stock, ptype, color):
        return False
    stock[ptype][color]["price"] = float(price)
    return True
