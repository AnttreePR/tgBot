"""Configuration module for the Telegram bot.

This module stores static configuration values used throughout the bot.
It includes the bot token and path to the main menu image. Adjust these
values to match your environment before running the bot.

Attributes:
    TOKEN (str): Telegram bot API token obtained from @BotFather.
    PHOTO_PATH (str): Absolute path to the image used in the main menu.

Usage:
    from .config import TOKEN, PHOTO_PATH
"""

# Replace the placeholder below with your actual bot token from @BotFather.
TOKEN: str = "8230454664:AAEJBTBa3Jp-A0VMa6dELf8JtCAuxn_Kf7A"

PHOTO_PATH: str = r"C:\Users\anttree\PycharmProjects\PythonProject\tgBot\images\ex.img.jpg"

# Твой Telegram ID (OWNER)
OWNER_ID: int = 936_977_024

# ID группы менеджеров (поставь сюда реальный chat_id группы)
# Обычно выглядит как отрицательное число, например: -1001234567890
MANAGER_CHAT_ID: int = -5275376289

COST_PER_MINUTE: float = 2.5   # ₽ за 1 минуту печати
SPOOL_GRAMS: int = 1000        # грамм в 1 катушке

# Контакты
CONTACT_PHONE = "+7 (999) 123-45-67"
CONTACT_EMAIL = "print@example.com"
CONTACT_TG = "@your_manager_username"
