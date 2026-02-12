"""Entry point for the Telegram bot.

This script initialises the TeleBot instance, registers all command and
callback handlers, and starts polling for updates. Run this file to
launch the bot.

Example:
    python bot.py
"""

import telebot

try:
    # Attempt relative imports when run as a module (e.g. `python -m tgBot.bot`)
    from .config import TOKEN  # type: ignore[import]
    from .handlers import register_all_handlers  # type: ignore[import]
except ImportError:
    # Fallback to absolute imports when executed as a script (e.g. `python bot.py`)
    from config import TOKEN  # type: ignore[import]
    from handlers import register_all_handlers  # type: ignore[import]


def main() -> None:
    """Create the bot, register handlers and start polling."""
    bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
    register_all_handlers(bot)
    # Start receiving updates via long polling. The none_stop=True option
    # ensures the bot continues running even after exceptions in handlers.
    bot.infinity_polling()


if __name__ == "__main__":
    main()
