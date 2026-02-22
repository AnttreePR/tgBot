import re
from telebot import TeleBot
from telebot.types import Message

from ..config import MANAGER_CHAT_ID
from ..roles import get_role, CUSTOMER
from ..order_state import is_order_active, stop_order

# message_id в группе -> customer_id
GROUP_TO_USER: dict[int, int] = {}

_CLOSE_RE = re.compile(r"^(?:/close|close|закрыть|закрой)\s+(\d+)\s*$", re.IGNORECASE)


def register_handlers(bot: TeleBot) -> None:
    """
    CUSTOMER ↔ менеджеры (через группу)

    - CUSTOMER пишет в личку -> в группу уходит ТОЛЬКО если включен ORDER_MODE
    - Любой участник группы может ответить reply -> бот отправит ответ клиенту
    - Закрытие: "/close <id>" или "закрыть <id>" (ID обязателен)
    """

    @bot.message_handler(
        func=lambda m: m.chat.type == "private",
        content_types=["text", "photo", "document", "voice", "video", "sticker"]
    )
    def customer_to_group(message: Message) -> None:
        # Только CUSTOMER
        if get_role(message.from_user.id) != CUSTOMER:
            return

        customer_id = message.from_user.id

        # Только если клиент нажал "Сделать заказ"
        if not is_order_active(customer_id):
            bot.send_message(customer_id, "Чтобы написать менеджеру, сначала нажми 🛒 «Сделать заказ».")
            return

        customer_name = (message.from_user.first_name or "").strip()
        customer_username = message.from_user.username

        header = "🆕 <b>Сообщение от клиента</b>\n"
        header += f"👤 {customer_name if customer_name else 'Без имени'}"
        if customer_username:
            header += f" (@{customer_username})"
        header += f"\n🆔 <code>{customer_id}</code>\n\n"
        header += f"Закрыть: <code>/close {customer_id}</code> или <code>закрыть {customer_id}</code>"

        # Шапка (тоже маппим)
        info_msg = bot.send_message(MANAGER_CHAT_ID, header, parse_mode="HTML")
        GROUP_TO_USER[info_msg.message_id] = customer_id

        # Копия сообщения клиента (маппим её тоже)
        try:
            copied = bot.copy_message(
                chat_id=MANAGER_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_to_message_id=info_msg.message_id
            )
            group_msg_id = copied.message_id if hasattr(copied, "message_id") else copied
            GROUP_TO_USER[group_msg_id] = customer_id
        except Exception:
            fwd = bot.forward_message(MANAGER_CHAT_ID, message.chat.id, message.message_id)
            GROUP_TO_USER[fwd.message_id] = customer_id

    @bot.message_handler(func=lambda m: m.chat.id == MANAGER_CHAT_ID, content_types=["text"])
    def group_router(message: Message) -> None:
        text = (message.text or "").strip()

        # Закрытие по команде с ID (reply не обязателен)
        m = _CLOSE_RE.match(text)
        if m:
            customer_id = int(m.group(1))
            stop_order(customer_id)

            try:
                bot.send_message(
                    customer_id,
                    "✅ Диалог закрыт.\n\n"
                    "Чтобы снова написать менеджеру — нажми 🛒 «Сделать заказ»."
                )
            except Exception:
                pass

            bot.reply_to(message, f"✅ Диалог закрыт для клиента {customer_id}")
            return

        # Обычный ответ клиенту: нужен reply на шапку/копию сообщения
        if not message.reply_to_message:
            return

        replied_id = message.reply_to_message.message_id
        customer_id = GROUP_TO_USER.get(replied_id)
        if not customer_id:
            return

        out = message.text.strip()
        if not out:
            return

        bot.send_message(customer_id, f"💬 Менеджер:\n\n{out}")
        bot.reply_to(message, "✅ Отправлено клиенту.")
