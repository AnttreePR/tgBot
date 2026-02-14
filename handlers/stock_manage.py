from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from ..roles import get_role, OWNER, OPERATOR
from ..keyboards import (
    stock_view_keyboard,
    stock_types_keyboard,
    stock_colors_keyboard,
    stock_qty_actions_keyboard,
    placeholder_keyboard,
)
from ..stock_data import get_default_stock
from ..stock_service import (
    load_stock,
    save_stock,
    add_or_update_plastic,
    delete_plastic,
    change_qty,
)
from ..stock_view import get_stock_pages


# user_id -> "new" | "del"
WAITING_INPUT: dict[int, str] = {}


def register_handlers(bot: TeleBot) -> None:
    def is_admin(user_id: int) -> bool:
        return get_role(user_id) in (OWNER, OPERATOR)

    def edit_caption_or_text(call: CallbackQuery, text: str, reply_markup=None) -> None:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        try:
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        except Exception:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )

    def get_stock():
        return load_stock(get_default_stock())

    def render_stock_page(call: CallbackQuery, page: int) -> None:
        stock = get_stock()
        pages = get_stock_pages(stock)
        total = max(1, len(pages))
        page = max(1, min(page, total))
        caption = pages[page - 1]
        kb = stock_view_keyboard(page, total)
        edit_caption_or_text(call, caption, kb)

    # ---------- VIEW STOCK ----------
    @bot.callback_query_handler(func=lambda c: c.data.startswith("stock_view:"))
    def cb_stock_view(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        WAITING_INPUT.pop(call.from_user.id, None)

        try:
            page = int(call.data.split(":")[1])
        except Exception:
            page = 1

        render_stock_page(call, page)
        bot.answer_callback_query(call.id)

    # ---------- QTY FLOW: CHOOSE TYPE ----------
    @bot.callback_query_handler(func=lambda c: c.data == "stock_qty:types")
    def cb_stock_qty_types(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        WAITING_INPUT.pop(call.from_user.id, None)

        stock = get_stock()
        types_list = sorted(stock.keys())

        text = "➕/➖ <b>Изменение количества</b>\n\nВыбери тип пластика:"
        kb = stock_types_keyboard(types_list, action="qty")
        edit_caption_or_text(call, text, kb)
        bot.answer_callback_query(call.id)

    # ---------- QTY FLOW: TYPE -> COLORS ----------
    @bot.callback_query_handler(func=lambda c: c.data.startswith("stock_qty_type:"))
    def cb_stock_qty_type(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        WAITING_INPUT.pop(call.from_user.id, None)

        ptype = call.data.split("stock_qty_type:", 1)[1]
        stock = get_stock()

        if ptype not in stock:
            bot.answer_callback_query(call.id, "Тип не найден")
            return

        colors = sorted(stock[ptype].keys())
        text = f"➕/➖ <b>{ptype}</b>\n\nВыбери цвет:"
        kb = stock_colors_keyboard(ptype, colors)
        edit_caption_or_text(call, text, kb)
        bot.answer_callback_query(call.id)

    # ---------- QTY FLOW: COLOR SELECTED -> ACTIONS ----------
    @bot.callback_query_handler(func=lambda c: c.data.startswith("stock_qty_color:"))
    def cb_stock_qty_color(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        WAITING_INPUT.pop(call.from_user.id, None)

        payload = call.data.split("stock_qty_color:", 1)[1]
        ptype, color = payload.split("|", 1)

        stock = get_stock()
        if ptype not in stock or color not in stock[ptype]:
            bot.answer_callback_query(call.id, "Позиция не найдена")
            return

        meta = stock[ptype][color]
        qty = int(meta.get("qty", 0))
        price = float(meta.get("price", 0))

        text = (
            f"📦 <b>{ptype}</b>\n"
            f"🎨 <b>{color}</b>\n\n"
            f"Количество: <b>{qty}</b> шт\n"
            f"Цена: <b>{price:.0f}</b> ₽/катушка\n\n"
            "Выбери действие:"
        )
        kb = stock_qty_actions_keyboard(ptype, color)
        edit_caption_or_text(call, text, kb)
        bot.answer_callback_query(call.id)

    # ---------- APPLY DELTA ----------
    @bot.callback_query_handler(func=lambda c: c.data.startswith("stock_qty_do:"))
    def cb_stock_qty_do(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        WAITING_INPUT.pop(call.from_user.id, None)

        payload = call.data.split("stock_qty_do:", 1)[1]
        ptype, color, delta_str = payload.split("|", 2)

        try:
            delta = int(delta_str)
        except Exception:
            bot.answer_callback_query(call.id, "Ошибка данных")
            return

        stock = get_stock()
        ok, new_qty = change_qty(stock, ptype, color, delta)
        if not ok:
            bot.answer_callback_query(call.id, "Позиция не найдена")
            return

        save_stock(stock)

        meta = stock[ptype][color]
        price = float(meta.get("price", 0))

        text = (
            "✅ <b>Обновлено</b>\n\n"
            f"📦 {ptype}\n"
            f"🎨 {color}\n"
            f"Новое количество: <b>{new_qty}</b> шт\n"
            f"Цена: <b>{price:.0f}</b> ₽/катушка"
        )
        kb = stock_qty_actions_keyboard(ptype, color)
        edit_caption_or_text(call, text, kb)
        bot.answer_callback_query(call.id, "Готово")

    # ---------- NEW PLASTIC: ASK INPUT ----------
    @bot.callback_query_handler(func=lambda c: c.data == "stock_new:ask")
    def cb_stock_new_ask(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        WAITING_INPUT[call.from_user.id] = "new"
        text = (
            "➕ <b>Новый пластик</b>\n\n"
            "Отправь одним сообщением в формате:\n"
            "<b>Тип|Цвет|Цена|Кол-во</b>\n\n"
            "Пример:\n"
            "<b>PLA Basic|Red|1431|12</b>\n\n"
            "Чтобы отменить — нажми «🔙 В меню»."
        )
        edit_caption_or_text(call, text, placeholder_keyboard())
        bot.answer_callback_query(call.id)

    # ---------- DELETE PLASTIC: ASK INPUT ----------
    @bot.callback_query_handler(func=lambda c: c.data == "stock_del:ask")
    def cb_stock_del_ask(call: CallbackQuery) -> None:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Доступ запрещён")
            return

        WAITING_INPUT[call.from_user.id] = "del"
        text = (
            "🗑️ <b>Удалить пластик</b>\n\n"
            "Отправь одним сообщением в формате:\n"
            "<b>Тип|Цвет</b>\n\n"
            "Пример:\n"
            "<b>PLA Basic|Mint Lime</b>\n\n"
            "Чтобы отменить — нажми «🔙 В меню»."
        )
        edit_caption_or_text(call, text, placeholder_keyboard())
        bot.answer_callback_query(call.id)

    # ---------- INPUT HANDLER (PRIVATE) ----------
    # ВАЖНО: ловим текст только если реально ждём ввод (new/del)
    @bot.message_handler(
        func=lambda m: m.chat.type == "private" and m.from_user and WAITING_INPUT.get(m.from_user.id) is not None,
        content_types=["text"],
    )
    def on_private_text(message: Message) -> None:
        user_id = message.from_user.id
        if not is_admin(user_id):
            return

        mode = WAITING_INPUT.get(user_id)
        if not mode:
            return

        text = (message.text or "").strip()

        # --- ADD / UPDATE ---
        if mode == "new":
            parts = [p.strip() for p in text.split("|")]
            if len(parts) != 4:
                bot.send_message(message.chat.id, "❌ Формат неверный. Нужно: Тип|Цвет|Цена|Кол-во")
                return

            ptype, color, price_str, qty_str = parts

            try:
                price = float(price_str.replace(",", "."))
                if price < 0:
                    price = 0
            except Exception:
                bot.send_message(message.chat.id, "❌ Цена должна быть числом. Пример: 1431")
                return

            try:
                qty = int(qty_str)
                if qty < 0:
                    qty = 0
            except Exception:
                bot.send_message(message.chat.id, "❌ Кол-во должно быть целым числом. Пример: 12")
                return

            stock = get_stock()
            add_or_update_plastic(stock, ptype, color, price, qty) 
            save_stock(stock)

            WAITING_INPUT.pop(user_id, None)
            bot.send_message(
                message.chat.id,
                f"✅ Добавлено/обновлено: {ptype} / {color}\n"
                f"Цена: {price:.0f} ₽/катушка\n"
                f"Количество: {qty} шт"
            )
            return

        # --- DELETE ---
        if mode == "del":
            parts = [p.strip() for p in text.split("|")]
            if len(parts) != 2:
                bot.send_message(message.chat.id, "❌ Формат неверный. Нужно: Тип|Цвет")
                return

            ptype, color = parts
            stock = get_stock()
            ok = delete_plastic(stock, ptype, color)
            if not ok:
                bot.send_message(message.chat.id, "⚠️ Не найдено. Проверь Тип и Цвет.")
                return

            save_stock(stock)
            WAITING_INPUT.pop(user_id, None)
            bot.send_message(message.chat.id, f"✅ Удалено: {ptype} / {color}")
            return
