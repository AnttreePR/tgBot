"""Start command handler for the Telegram bot.

This module registers a handler for the `/start` command. When a user
invokes this command, the bot greets them with a welcome message and
displays the main menu. The menu options are determined by the user's
role, which is looked up via the `get_role` function.

Usage:
    from telebot import TeleBot
    from .start import register_handlers

    bot = TeleBot(TOKEN)
    register_handlers(bot)
"""

from telebot import TeleBot
from telebot.types import Message

from ..config import PHOTO_PATH
from ..roles import get_role
from ..keyboards import main_menu_keyboard


def register_handlers(bot: TeleBot) -> None:
    """Register the `/start` command handler with the provided bot instance.

    Args:
        bot: The TeleBot instance to register the handler on.
    """

    @bot.message_handler(commands=["start"])
    def handle_start(message: Message) -> None:
        """Respond to the /start command.

        Sends the main menu photo with a caption tailored to the user's role.
        """
        chat_id = message.chat.id
        user_id = message.from_user.id
        role = get_role(user_id)
        # Compose a generic welcome message. You can personalise this if
        # desired, for example by including the user's first name.
        caption = (
            "Добро пожаловать в управление 3D‑фермой!\n\n"
            "Выберите нужный пункт меню."
        )
        # Open the image file in binary mode. It is important to open the
        # file inside the handler so that file handles are not left open.
        try:
            with open(PHOTO_PATH, "rb") as photo:
                bot.send_photo(
                    chat_id,
                    photo,
                    caption=caption,
                    reply_markup=main_menu_keyboard(role),
                )
        except FileNotFoundError:
            # Fallback in case the image cannot be found; send text only
            bot.send_message(
                chat_id,
                caption,
                reply_markup=main_menu_keyboard(role),
            )
