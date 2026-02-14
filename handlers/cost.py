from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from ..config import COST_PER_MINUTE, SPOOL_GRAMS
from ..roles import get_role, OWNER, OPERATOR
from ..keyboards import cost_start_keyboard, cost_colors_keyboard, cost_back_keyboard
from ..stock_data import get_default_stock
from ..stock_service import load_stock


# state: user_id -> {"step": "...", ...}
# step: "plastic" | "grams" | "minutes"
COST_STATE = {}


def register_handlers(bot: TeleBot) -> None:
    def is_admin(user_id: int) -> bool:
        return get_role(user_id) in (OWNER, OPERATOR)

    def edit_caption_or_text(call: CallbackQuery, text: str, reply_markup=None) -> None:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=text, reply_markup=reply_markup)
        except Exception:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)

    def get_stock():
        return load_stock(get_default_stock())

    # старт себестоимости
    @bot.callback_query_handler(func=lambda c: c.data == "cost_start")
    def cb_cost_start(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        stock = get_stock()
        types_list = sorted(stock.keys())

        COST_STATE[call.from_user.id] = {"step": "plastic"}

        text = (
            "💰 Себестоимость\n\n"
            "1) Выбери пластик кнопками ИЛИ введи сообщением:\n"
            "<b>Тип|Цвет</b>\n"
            "Пример: <b>PLA Basic|Mint Lime</b>\n\n"
            f"Константа времени: {COST_PER_MINUTE} ₽/минута\n"
            f"Катушка: {SPOOL_GRAMS} г\n"
        )
        edit_caption_or_text(call, text, cost_start_keyboard(types_list))
        bot.answer_callback_query(call.id)

    # выбор типа -> показать цвета
    @bot.callback_query_handler(func=lambda c: c.data.startswith("cost_type:"))
    def cb_cost_type(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        ptype = call.data.split("cost_type:", 1)[1]
        stock = get_stock()
        if ptype not in stock:
            bot.answer_callback_query(call.id, "Тип не найден")
            return

        colors = sorted(stock[ptype].keys())
        text = f"💰 Себестоимость\n\nТип: <b>{ptype}</b>\nВыбери цвет:"
        edit_caption_or_text(call, text, cost_colors_keyboard(ptype, colors))
        bot.answer_callback_query(call.id)

    # выбран цвет -> ждём граммы
    @bot.callback_query_handler(func=lambda c: c.data.startswith("cost_color:"))
    def cb_cost_color(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        payload = call.data.split("cost_color:", 1)[1]
        ptype, color = payload.split("|", 1)

        stock = get_stock()
        if ptype not in stock or color not in stock[ptype]:
            bot.answer_callback_query(call.id, "Пластик не найден")
            return

        COST_STATE[call.from_user.id] = {"step": "grams", "ptype": ptype, "color": color}

        meta = stock[ptype][color]
        price_per_spool = float(meta.get("price", 0))
        price_per_gram = price_per_spool / float(SPOOL_GRAMS)

        text = (
            "💰 Себестоимость\n\n"
            f"Пластик: <b>{ptype}</b> / <b>{color}</b>\n"
            f"Цена: <b>{price_per_spool:.0f} ₽/катушка</b> (~{price_per_gram:.3f} ₽/г)\n\n"
            "2) Введи расход в граммах (пример: <b>85</b>)"
        )
        edit_caption_or_text(call, text, cost_back_keyboard())
        bot.answer_callback_query(call.id)

    # текстовый ввод (в личке): пластик/граммы/минуты
    @bot.message_handler(func=lambda m: m.chat.type == "private", content_types=["text"])
    def cost_text(message: Message) -> None:
        user_id = message.from_user.id
        if not is_admin(user_id):
            return

        st = COST_STATE.get(user_id)
        if not st:
            return

        text = (message.text or "").strip()

        # 1) пластик текстом "Тип|Цвет"
        if st.get("step") == "plastic":
            parts = [p.strip() for p in text.split("|")]
            if len(parts) != 2:
                bot.send_message(message.chat.id, "❌ Формат: Тип|Цвет. Пример: PLA Basic|Mint Lime")
                return

            ptype, color = parts
            stock = get_stock()
            if ptype not in stock or color not in stock[ptype]:
                bot.send_message(message.chat.id, "❌ Такого пластика нет в складе. Проверь тип/цвет.")
                return

            COST_STATE[user_id] = {"step": "grams", "ptype": ptype, "color": color}
            bot.send_message(message.chat.id, "✅ Ок. Теперь введи расход в граммах (например 85).")
            return

        # 2) граммы
        if st.get("step") == "grams":
            try:
                grams = float(text.replace(",", "."))
                if grams <= 0:
                    raise ValueError
            except Exception:
                bot.send_message(message.chat.id, "❌ Граммы должны быть числом > 0. Пример: 85")
                return

            st["grams"] = grams
            st["step"] = "minutes"
            COST_STATE[user_id] = st

            bot.send_message(message.chat.id, "✅ Ок. Теперь введи время печати в минутах (например 120).")
            return

        # 3) минуты -> расчёт
        if st.get("step") == "minutes":
            try:
                minutes = float(text.replace(",", "."))
                if minutes < 0:
                    raise ValueError
            except Exception:
                bot.send_message(message.chat.id, "❌ Минуты должны быть числом >= 0. Пример: 120")
                return

            stock = get_stock()
            ptype = st["ptype"]
            color = st["color"]
            grams = float(st["grams"])

            meta = stock[ptype][color]
            price_per_spool = float(meta.get("price", 0))

            price_per_gram = price_per_spool / float(SPOOL_GRAMS)
            material_cost = grams * price_per_gram
            time_cost = minutes * float(COST_PER_MINUTE)
            total = material_cost + time_cost

            bot.send_message(
                message.chat.id,
                "💰 Себестоимость\n\n"
                f"Пластик: {ptype} / {color}\n"
                f"Цена: {price_per_spool:.0f} ₽/катушка ({price_per_gram:.3f} ₽/г)\n"
                f"Расход: {grams:.1f} г\n"
                f"Время: {minutes:.1f} мин\n\n"
                f"Материал: {material_cost:.2f} ₽\n"
                f"Время: {time_cost:.2f} ₽\n"
                f"Итого: <b>{total:.2f} ₽</b>"
            )

            COST_STATE.pop(user_id, None)
            return
