"""Additional command handlers for the Telegram bot.

This module contains handlers for custom commands beyond `/start`. For
now, it defines a stub for the `/help` command. Additional commands can
be added here as the bot's functionality grows.
"""

from telebot import TeleBot
from telebot.types import Message

from ..roles import get_role
from ..keyboards import main_menu_keyboard


def register_handlers(bot: TeleBot) -> None:
    """Register custom command handlers on the provided bot instance."""

    @bot.message_handler(commands=["help"])
    def handle_help(message: Message) -> None:
        """Provide a help message describing available commands."""
        role = get_role(message.from_user.id)
        # Basic help text; you can tailor this per role if needed
        text = (
            "Помощь:\n"
            "— /start — открыть главное меню\n"
            "— /help — показать это сообщение"
        )
        bot.reply_to(message, text, reply_markup=main_menu_keyboard(role))

    @bot.message_handler(commands=["chatid"])
    def handle_chatid(message: Message) -> None:
        bot.reply_to(message, f"chat_id: {message.chat.id}")
