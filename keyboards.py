"""Factory functions for building inline keyboards.

All inline keyboards used in the bot are defined here. Centralising
keyboard creation makes it easier to manage callback identifiers and
ensure a consistent look and feel throughout the application.

Functions:
    main_menu_keyboard(role: str) -> InlineKeyboardMarkup: Build the main
        menu for a given user role.
    stock_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
        Build pagination controls for the stock view.
    placeholder_keyboard(text: str) -> InlineKeyboardMarkup: Helper for
        stubbed features, showing a single back button.
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from .roles import OWNER, OPERATOR, CUSTOMER


def main_menu_keyboard(role: str) -> InlineKeyboardMarkup:
    """Create the main menu inline keyboard based on user role.

    Args:
        role: The user's role (OWNER, OPERATOR or CUSTOMER).

    Returns:
        InlineKeyboardMarkup: A keyboard with appropriate menu options.
    """
    markup = InlineKeyboardMarkup(row_width=1)
    # Administrative functions available to owners and operators
    if role in (OWNER, OPERATOR):
        markup.add(
            InlineKeyboardButton("📦 Склад", callback_data="stock_1"),
            InlineKeyboardButton("🗑️ Списание пластика", callback_data="writeoff"),
        )
        # Only owners see the cost price option
        if role == OWNER:
            markup.add(
                InlineKeyboardButton("💰 Себестоимость", callback_data="cost"),
            )
    # Customer‑facing functions
    if role == CUSTOMER:
        markup.add(
            InlineKeyboardButton("🛒 Сделать заказ", callback_data="create_order"),
            InlineKeyboardButton("📦 Мои заказы", callback_data="my_orders"),
        )
    return markup


def stock_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Create pagination controls for the stock pages.

    Args:
        current_page: The index of the page currently being displayed (1‑based).
        total_pages: The total number of pages available.

    Returns:
        InlineKeyboardMarkup: A keyboard with back/forward buttons and a
            button to return to the main menu.
    """
    markup = InlineKeyboardMarkup()
    # Navigation row: previous and next buttons as appropriate
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"stock_{current_page - 1}")
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("➡️ Вперёд", callback_data=f"stock_{current_page + 1}")
        )
    if nav_buttons:
        # Add navigation buttons on the same row
        markup.row(*nav_buttons)
    # Back to menu button on its own row
    markup.add(
        InlineKeyboardButton("🔙 В меню", callback_data="back_to_menu")
    )
    return markup


def placeholder_keyboard() -> InlineKeyboardMarkup:
    """Return a keyboard for stubbed features with only a back button.

    This helper is used for features that are not yet implemented. It
    provides a single button to return to the main menu.

    Returns:
        InlineKeyboardMarkup: A keyboard containing a back button.
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 В меню", callback_data="back_to_menu"))
    return markup
