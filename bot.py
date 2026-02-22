"""Entry point for the Telegram bot."""

import telebot

from .config import TOKEN
from .handlers import register_all_handlers


def main() -> None:
    bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
    register_all_handlers(bot)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
