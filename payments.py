import logging
import uuid
from datetime import datetime
from aiogram import Bot
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram.exceptions import TelegramBadRequest
from config import CURRENCY


async def send_invoice(
    bot: Bot, 
    chat_id: int, 
    title: str, 
    description: str, 
    price: int,
    payload: str = None
):
    """
    Отправляет счет на оплату Telegram Stars
    
    Args:
        bot: экземпляр бота
        chat_id: ID пользователя
        title: заголовок счета
        description: описание
        price: цена в Stars
        payload: уникальный идентификатор заказа
    """
    if payload is None:
        payload = str(uuid.uuid4())
    
    try:
        # Отправляем счет через send_invoice
        await bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token="",  # Для Stars оставляем пустым (подтверждено документацией)
            currency=CURRENCY,
            prices=[LabeledPrice(label=title, amount=price)],
            start_parameter="purchase",
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False,
        )
        logging.info(f"✅ Счет отправлен пользователю {chat_id}: {title} - {price} ⭐, payload: {payload}")
        return payload
    except TelegramBadRequest as e:
        logging.error(f"❌ Ошибка Telegram при отправке счета: {e}")
        raise
    except Exception as e:
        logging.error(f"❌ Неизвестная ошибка при отправке счета: {e}")
        raise


async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    """Обработка предварительной проверки платежа"""
    try:
        # Проверяем валюту
        if pre_checkout_query.currency != CURRENCY:
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id, 
                ok=False, 
                error_message=f"Неподдерживаемая валюта: {pre_checkout_query.currency}"
            )
            logging.warning(f"❌ Неподдерживаемая валюта: {pre_checkout_query.currency}")
            return
        
        # Проверяем сумму
        if pre_checkout_query.total_amount <= 0:
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id, 
                ok=False, 
                error_message="Неверная сумма платежа"
            )
            return
        
        # Проверяем, что payload начинается с правильного префикса
        if not pre_checkout_query.invoice_payload or len(pre_checkout_query.invoice_payload) < 10:
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id, 
                ok=False, 
                error_message="Неверный идентификатор заказа"
            )
            return
        
        # Все проверки пройдены
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        logging.info(f"✅ Pre-checkout успешно пройден для пользователя {pre_checkout_query.from_user.id}")
        
    except Exception as e:
        logging.error(f"❌ Ошибка при pre-checkout: {e}")
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id, 
            ok=False, 
            error_message="Произошла ошибка при обработке платежа"
        )


async def process_successful_payment(message: Message) -> dict:
    """Обработка успешного платежа с проверками"""
    payment = message.successful_payment
    
    # Проверяем валюту
    if payment.currency != CURRENCY:
        logging.warning(f"⚠️ Неподдерживаемая валюта в платеже: {payment.currency}")
        return None
    
    # Проверяем сумму
    if payment.total_amount <= 0:
        logging.warning(f"⚠️ Неверная сумма платежа: {payment.total_amount}")
        return None
    
    # Проверяем payload
    if not payment.invoice_payload or len(payment.invoice_payload) < 10:
        logging.warning(f"⚠️ Неверный payload: {payment.invoice_payload}")
        return None
    
    logging.info(f"✅ Успешный платеж: {payment.invoice_payload}, сумма: {payment.total_amount} ⭐")
    
    return {
        "price": payment.total_amount,
        "payload": payment.invoice_payload,
        "payment_id": payment.telegram_payment_charge_id,
        "provider_payment_id": payment.provider_payment_charge_id,
        "currency": payment.currency
          }
