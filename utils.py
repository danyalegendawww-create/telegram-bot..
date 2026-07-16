from datetime import datetime
import pytz
import re


def get_moscow_time() -> str:
    """Возвращает текущее время в Москве в формате DD.MM.YYYY HH:MM"""
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz)
    return now.strftime("%d.%m.%Y %H:%M")


def validate_minecraft_nickname(nickname: str) -> bool:
    """Проверяет ник Minecraft на валидность"""
    if not nickname or len(nickname) < 2 or len(nickname) > 16:
        return False
    # Разрешены только буквы, цифры и подчеркивание
    return bool(re.match(r'^[a-zA-Z0-9_]{2,16}$', nickname))


def format_admin_message(
    username: str, 
    user_id: int, 
    nickname: str, 
    purchase_type: str, 
    price: int, 
    time_str: str, 
    payment_id: str = None,
    order_id: str = None
) -> str:
    """Форматирует сообщение для администраторов"""
    message = (
        f"🆕 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 Игрок: {nickname}\n"
        f"📦 Тип: {purchase_type}\n"
        f"💰 Сумма: {price} ⭐\n"
        f"🕐 Время (МСК): {time_str}\n"
        f"🆔 Telegram ID: {user_id}\n"
        f"👤 @{username or 'нет username'}"
    )
    
    if order_id:
        message += f"\n🆔 Номер заказа: {order_id}"
    
    if payment_id and payment_id != "Неизвестно":
        message += f"\n🆔 ID платежа: {payment_id}"
    
    return message
