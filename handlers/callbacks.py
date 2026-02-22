from telebot import TeleBot
from telebot.types import CallbackQuery

from ..roles import get_role, CUSTOMER
from ..keyboards import main_menu_keyboard, placeholder_keyboard
from ..order_state import start_order
from ..config import CONTACT_PHONE, CONTACT_EMAIL, CONTACT_TG


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

    @bot.callback_query_handler(func=lambda call: call.data == "create_order")
    def handle_create_order(call: CallbackQuery) -> None:
        # Доступ только CUSTOMER
        if get_role(call.from_user.id) != CUSTOMER:
            bot.answer_callback_query(call.id, "⛔️ Нет доступа", show_alert=True)
            return

        # Включаем ORDER_MODE для этого клиента
        start_order(call.from_user.id)

        caption = (
            "🛒 <b>Оформление заказа</b>\n\n"
            "Привет! 👋\n"
            "Напиши сюда, что нужно напечатать (ссылка/фото/файл STL/описание), "
            "размер, цвет пластика и количество.\n\n"
            "✅ Сообщение увидит менеджер.\n"
            "💬 В ближайшее время менеджер напишет тебе в этот чат."
        )
        edit_caption_or_text(call, caption, placeholder_keyboard())
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "contacts")
    def handle_contacts(call: CallbackQuery) -> None:
        # Доступ только CUSTOMER
        if get_role(call.from_user.id) != CUSTOMER:
            bot.answer_callback_query(call.id, "⛔️ Нет доступа", show_alert=True)
            return

        caption = (
            "📇 <b>Контакты</b>\n\n"
            f"📞 Телефон: <code>{CONTACT_PHONE}</code>\n"
            f"✉️ Почта: <code>{CONTACT_EMAIL}</code>\n"
            f"💬 Telegram: <code>{CONTACT_TG}</code>\n\n"
            "Чтобы оформить заказ — нажми 🛒 «Сделать заказ»."
        )
        edit_caption_or_text(call, caption, placeholder_keyboard())
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "help_customer")
    def handle_help_customer(call: CallbackQuery) -> None:
        # Доступ только CUSTOMER
        if get_role(call.from_user.id) != CUSTOMER:
            bot.answer_callback_query(call.id, "⛔️ Нет доступа", show_alert=True)
            return

        caption = (
            "🆘 <b>Помощь</b>\n\n"
            "Чтобы сделать заказ — нажми «Сделать заказ» и просто напиши сообщение.\n"
            "Менеджер ответит в этом чате."
        )
        edit_caption_or_text(call, caption, placeholder_keyboard())
        bot.answer_callback_query(call.id)
