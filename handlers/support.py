from telebot import TeleBot
from telebot.types import Message

from ..config import MANAGER_CHAT_ID
from ..roles import get_role, OWNER, OPERATOR, CUSTOMER

# Память: message_id в группе -> customer_id
# (если бот перезапустится — связи сотрутся, но для старта идеально)
GROUP_MSG_TO_CUSTOMER = {}


def register_handlers(bot: TeleBot) -> None:
    """
    План B:
    - CUSTOMER пишет боту в личку -> бот копирует/пересылает в группу менеджеров
    - OWNER/OPERATOR отвечают реплаем на сообщение в группе -> бот отправляет ответ клиенту
    """

    @bot.message_handler(func=lambda m: m.chat.type == "private", content_types=["text", "photo", "document", "voice", "video", "sticker"])
    def customer_to_group(message: Message) -> None:
        # В личке принимаем сообщения от клиентов (и вообще от всех)
        role = get_role(message.from_user.id)

        # Если это не CUSTOMER — не пересылаем (иначе ты сам себе в группу начнёшь сыпать)
        if role != CUSTOMER:
            return

        customer_id = message.from_user.id
        customer_name = (message.from_user.first_name or "").strip()
        customer_username = message.from_user.username

        header = "🆕 Сообщение от клиента\n"
        header += f"👤 {customer_name if customer_name else 'Без имени'}"
        if customer_username:
            header += f" (@{customer_username})"
        header += f"\n🆔 {customer_id}\n\n"

        # 1) Сначала отправим “шапку” текстом
        info_msg = bot.send_message(MANAGER_CHAT_ID, header)

        # 2) Затем скопируем/перешлём само сообщение
        # Копирование лучше, потому что оно работает для разных типов и не “ломает” оформление.
        # Но reply_to_message.forward_from может не быть.
        # Поэтому мы храним mapping: msg_id в группе -> customer_id.
        try:
            copied = bot.copy_message(
                chat_id=MANAGER_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_to_message_id=info_msg.message_id
            )
            # copy_message возвращает message_id (int) в pyTelegramBotAPI
            # Но иногда может вернуть Message — зависит от версии.
            group_msg_id = copied.message_id if hasattr(copied, "message_id") else copied
            GROUP_MSG_TO_CUSTOMER[group_msg_id] = customer_id

        except Exception:
            # Фоллбек: если copy_message недоступен/сломался — просто forward
            fwd = bot.forward_message(MANAGER_CHAT_ID, message.chat.id, message.message_id)
            GROUP_MSG_TO_CUSTOMER[fwd.message_id] = customer_id

        # Клиенту можно подтверждение (по желанию)
        bot.send_message(customer_id, "✅ Сообщение отправлено менеджеру. Мы скоро ответим.")

    @bot.message_handler(func=lambda m: m.chat.id == MANAGER_CHAT_ID, content_types=["text"])
    def manager_reply_to_customer(message: Message) -> None:
        # Это обработчик сообщений В ГРУППЕ менеджеров
        role = get_role(message.from_user.id)
        if role not in (OWNER, OPERATOR):
            return

        # Отвечать клиенту можно только reply-ем на сообщение (иначе непонятно кому)
        if not message.reply_to_message:
            return

        replied_id = message.reply_to_message.message_id

        # Пытаемся найти customer_id по message_id, на который отвечают
        customer_id = GROUP_MSG_TO_CUSTOMER.get(replied_id)

        # Иногда менеджер отвечает не на копию, а на “шапку” (info_msg),
        # тогда попробуем заглянуть на уровень ниже: reply_to_message может быть "шапка",
        # а под ней было пересланное/скопированное сообщение.
        if not customer_id:
            # Пытаемся найти по цепочке: если ответили на "шапку", то под ней обычно есть reply
            # Но Telegram не даёт нам список ответов. Поэтому тут честно сообщаем.
            bot.reply_to(message, "⚠️ Не могу определить клиента. Ответьте реплаем на сообщение клиента (копию/пересылку).")
            return

        # Отправляем текст клиенту
        text = message.text.strip()
        if not text:
            return

        bot.send_message(customer_id, f"💬 Ответ менеджера:\n\n{text}")

        # В группе отметим, что отправлено
        bot.reply_to(message, "✅ Отправлено клиенту.")
