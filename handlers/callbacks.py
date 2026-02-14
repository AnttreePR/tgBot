from telebot import TeleBot
from telebot.types import CallbackQuery

from ..roles import get_role
from ..keyboards import main_menu_keyboard, placeholder_keyboard


def register_handlers(bot: TeleBot) -> None:

    def edit_caption_or_text(call: CallbackQuery, text: str, reply_markup=None) -> None:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=text, reply_markup=reply_markup)
        except Exception:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
    def handle_back_to_menu(call: CallbackQuery) -> None:
        role = get_role(call.from_user.id)
        caption = "Главное меню:\n\nВыберите пункт."
        edit_caption_or_text(call, caption, main_menu_keyboard(role))
        bot.answer_callback_query(call.id)

    # CUSTOMER заглушки
    @bot.callback_query_handler(func=lambda call: call.data == "create_order")
    def handle_create_order(call: CallbackQuery) -> None:
        caption = "🛒 Создание заказа — пока в разработке."
        edit_caption_or_text(call, caption, placeholder_keyboard())
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "my_orders")
    def handle_my_orders(call: CallbackQuery) -> None:
        caption = "📦 Мои заказы — пока в разработке."
        edit_caption_or_text(call, caption, placeholder_keyboard())
        bot.answer_callback_query(call.id)
