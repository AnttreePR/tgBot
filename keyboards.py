from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from .roles import OWNER, OPERATOR, CUSTOMER


def main_menu_keyboard(role: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)

    # OWNER/OPERATOR: только 2 кнопки
    if role in (OWNER, OPERATOR):
        markup.add(
            InlineKeyboardButton("📦 Склад", callback_data="stock_view:1"),
            InlineKeyboardButton("💰 Себестоимость", callback_data="cost_start"),
        )
        return markup

    # CUSTOMER (как было)
    markup.add(
        InlineKeyboardButton("🛒 Сделать заказ", callback_data="create_order"),
        InlineKeyboardButton("📦 Мои заказы", callback_data="my_orders"),
    )
    return markup


def placeholder_keyboard() -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🔙 В меню", callback_data="back_to_menu"))
    return m


# ---------- Себестоимость ----------

def cost_start_keyboard(types_list: list[str]) -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup(row_width=1)
    for t in types_list:
        m.add(InlineKeyboardButton(t, callback_data=f"cost_type:{t}"))
    m.add(InlineKeyboardButton("🔙 В меню", callback_data="back_to_menu"))
    return m


def cost_colors_keyboard(ptype: str, colors: list[str]) -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup(row_width=1)
    for c in colors:
        m.add(InlineKeyboardButton(c, callback_data=f"cost_color:{ptype}|{c}"))
    m.add(InlineKeyboardButton("🔙 Назад", callback_data="cost_start"))
    m.add(InlineKeyboardButton("🔙 В меню", callback_data="back_to_menu"))
    return m


def cost_back_keyboard() -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🔙 В меню", callback_data="back_to_menu"))
    return m


# ---------- Склад (если у тебя уже есть свои — можешь оставить, но этот вариант рабочий) ----------

def stock_view_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup()
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"stock_view:{page-1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"stock_view:{page+1}"))
    if nav:
        m.row(*nav)

    m.add(
        InlineKeyboardButton("➕/➖ Изменить количество", callback_data="stock_qty:types"),
        InlineKeyboardButton("➕ Новый пластик", callback_data="stock_new:ask"),
        InlineKeyboardButton("🗑️ Удалить пластик", callback_data="stock_del:ask"),
        InlineKeyboardButton("🔙 В меню", callback_data="back_to_menu"),
    )
    return m


def stock_types_keyboard(types_list: list[str], action: str) -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup(row_width=1)
    for t in types_list:
        m.add(InlineKeyboardButton(t, callback_data=f"stock_{action}_type:{t}"))
    m.add(InlineKeyboardButton("🔙 Назад", callback_data="stock_view:1"))
    return m


def stock_colors_keyboard(ptype: str, colors: list[str]) -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup(row_width=1)
    for c in colors:
        m.add(InlineKeyboardButton(c, callback_data=f"stock_qty_color:{ptype}|{c}"))
    m.add(InlineKeyboardButton("🔙 Назад", callback_data="stock_qty:types"))
    return m


def stock_qty_actions_keyboard(ptype: str, color: str) -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton("+1", callback_data=f"stock_qty_do:{ptype}|{color}|1"),
        InlineKeyboardButton("+5", callback_data=f"stock_qty_do:{ptype}|{color}|5"),
        InlineKeyboardButton("+10", callback_data=f"stock_qty_do:{ptype}|{color}|10"),
    )
    m.row(
        InlineKeyboardButton("-1", callback_data=f"stock_qty_do:{ptype}|{color}|-1"),
        InlineKeyboardButton("-5", callback_data=f"stock_qty_do:{ptype}|{color}|-5"),
        InlineKeyboardButton("-10", callback_data=f"stock_qty_do:{ptype}|{color}|-10"),
    )
    m.add(InlineKeyboardButton("🔙 Назад", callback_data=f"stock_qty_type:{ptype}"))
    m.add(InlineKeyboardButton("📦 К просмотру", callback_data="stock_view:1"))
    return m
