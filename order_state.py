from threading import RLock

_active_orders: set[int] = set()
_lock = RLock()


def start_order(user_id: int) -> None:
    """Включить режим оформления заказа для пользователя."""
    with _lock:
        _active_orders.add(user_id)


def stop_order(user_id: int) -> None:
    """Выключить режим оформления заказа для пользователя."""
    with _lock:
        _active_orders.discard(user_id)


def is_order_active(user_id: int) -> bool:
    """Проверить, включен ли режим оформления заказа."""
    with _lock:
        return user_id in _active_orders
