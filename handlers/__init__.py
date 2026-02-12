from telebot import TeleBot

from .start import register_handlers as register_start
from .callbacks import register_handlers as register_callbacks
from .commands import register_handlers as register_commands
from .support import register_handlers as register_support


def register_all_handlers(bot: TeleBot) -> None:
    register_start(bot)
    register_callbacks(bot)
    register_commands(bot)
    register_support(bot)
