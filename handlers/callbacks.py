"""Callback query handlers for inline keyboards.

This module registers handlers for various callback_data strings used
throughout the bot. It includes pagination for the stock view, returns
the user to the main menu, and stubs out placeholders for yet‑to‑be
implemented features like writing off filament or viewing cost price.

Role checks are performed on administrative callbacks to ensure only
authorised users can access restricted functions. If a user attempts to
invoke a restricted callback, they receive an alert via
`answer_callback_query` and the request is ignored.
"""

from telebot import TeleBot
from telebot.types import CallbackQuery

from ..roles import get_role, OWNER, OPERATOR
from ..stock_view import get_stock_pages
from ..keyboards import (
    main_menu_keyboard,
    stock_keyboard,
    placeholder_keyboard,
)

def register_handlers(bot: TeleBot) -> None:
    """Register callback query handlers on the provided bot instance."""

    # Cache stock pages to avoid rebuilding them on every callback. If the
    # stock changes during runtime and you need live updates, consider
    # regenerating this cache or storing state elsewhere.
    stock_pages = get_stock_pages()
    total_pages = len(stock_pages)

    def edit_caption_or_text(chat_id: int, message_id: int, text: str, reply_markup=None) -> None:
        """Edit either the caption or text of a message.

        Telegram provides separate methods for editing captions and texts. This
        helper attempts to edit the caption first; if that fails (for
        example, if the message has no media), it falls back to editing
        the text.

        Args:
            chat_id: Identifier of the chat containing the message.
            message_id: Identifier of the message to edit.
            text: New caption or text for the message.
            reply_markup: Inline keyboard markup to attach to the edited message.
        """
        try:
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=text,
                reply_markup=reply_markup,
            )
        except Exception:
            # When editing text, the parameter name is 'text' instead of 'caption'
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("stock_"))
    def handle_stock(call: CallbackQuery) -> None:
        """Display a specific page of the stock inventory.

        Only users with OWNER or OPERATOR roles can view the stock. If an
        unauthorised user triggers this callback, they receive an error alert.
        The page number is parsed from the callback_data (e.g. 'stock_2').
        """
        user_id = call.from_user.id
        role = get_role(user_id)
        if role not in (OWNER, OPERATOR):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return
        # Extract page number from callback data, defaulting to 1 if parsing fails
        try:
            _, page_str = call.data.split("_")
            page = int(page_str)
        except (ValueError, IndexError):
            page = 1
        # Clamp page to the valid range
        page = max(1, min(page, total_pages))
        caption = stock_pages[page - 1]
        # Build pagination keyboard and update the message
        markup = stock_keyboard(page, total_pages)
        edit_caption_or_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=caption,
            reply_markup=markup,
        )
        # Acknowledge the callback to prevent Telegram's loading indicator
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
    def handle_back_to_menu(call: CallbackQuery) -> None:
        """Return the user to the main menu from any sub‑menu."""
        user_id = call.from_user.id
        role = get_role(user_id)
        caption = (
            "Добро пожаловать в управление 3D‑фермой!\n\n"
            "Выберите нужный пункт меню."
        )
        markup = main_menu_keyboard(role)
        edit_caption_or_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=caption,
            reply_markup=markup,
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "writeoff")
    def handle_writeoff(call: CallbackQuery) -> None:
        """Stub for the plastic write‑off feature.

        Accessible only to owners and operators. Displays a placeholder
        message along with a back button. Real implementation would involve
        updating stock quantities.
        """
        user_id = call.from_user.id
        role = get_role(user_id)
        if role not in (OWNER, OPERATOR):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return
        caption = (
            "Списание пластика — функция пока не реализована.\n\n"
            "Пожалуйста, вернитесь в меню."
        )
        markup = placeholder_keyboard()
        edit_caption_or_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=caption,
            reply_markup=markup,
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "cost")
    def handle_cost(call: CallbackQuery) -> None:
        """Stub for the cost price feature.

        Only the owner should access this callback. It displays a placeholder
        explaining that the feature is under development.
        """
        user_id = call.from_user.id
        role = get_role(user_id)
        if role != OWNER:
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return
        caption = (
            "Расчёт себестоимости — функция пока не реализована.\n\n"
            "Пожалуйста, вернитесь в меню."
        )
        markup = placeholder_keyboard()
        edit_caption_or_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=caption,
            reply_markup=markup,
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "create_order")
    def handle_create_order(call: CallbackQuery) -> None:
        """Stub for the order creation feature.

        This placeholder is displayed when a customer wants to create a new
        order. In a full implementation, this would guide the user
        through selecting the filament type, colour and quantity, then
        collecting contact details.
        """
        caption = (
            "Создание заказа — функция пока не реализована.\n\n"
            "Пожалуйста, вернитесь в меню."
        )
        markup = placeholder_keyboard()
        edit_caption_or_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=caption,
            reply_markup=markup,
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "my_orders")
    def handle_my_orders(call: CallbackQuery) -> None:
        """Stub for viewing a customer's existing orders."""
        caption = (
            "Просмотр заказов — функция пока не реализована.\n\n"
            "Пожалуйста, вернитесь в меню."
        )
        markup = placeholder_keyboard()
        edit_caption_or_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=caption,
            reply_markup=markup,
        )
        bot.answer_callback_query(call.id)
