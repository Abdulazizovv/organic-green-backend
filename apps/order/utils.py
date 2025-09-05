"""Utility functions for order related operations (notifications etc.)"""
import asyncio
import logging
from decimal import Decimal
from typing import Iterable, Optional
import aiohttp
from django.db import transaction
from django.db.models import F

from apps.botapp.models import BotUser
from bot.data.config import BOT_TOKEN
from .models import Order

logger = logging.getLogger(__name__)

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

STATUS_MESSAGES = {
    'pending': "⏳ Buyurtmangiz qabul qilindi va tasdiqlash jarayonida.",
    'paid': "💳 To'lovingiz qabul qilindi. Rahmat! Buyurtma tayyorlanishga yuborildi.",
    'processing': "🛠 Buyurtmangiz hozir tayyorlanmoqda.",
    'shipped': "🚚 Buyurtmangiz jo'natildi. Tez orada yetib boradi.",
    'delivered': "✅ Buyurtmangiz yetkazib berildi. Yaxshi foydalanishingizni tilaymiz!",
    'canceled': "❌ Buyurtma bekor qilindi. Savollar bo'lsa murojaat qiling.",
}

CUSTOMER_HEADER_ICON = "🟢"


def format_price(value: Decimal) -> str:
    try:
        return f"{value:,.2f}".replace(',', ' ').rstrip('0').rstrip('.')
    except Exception:
        return str(value)


def build_order_message(order: Order) -> str:
    full_name = order.full_name or (order.user.get_full_name() if order.user else 'Noma`lum')
    phone = order.contact_phone or (getattr(order.user, 'phone', None) if order.user else None) or '—'
    lines = [
        "🛍 Yangi buyurtma!",
        f"Raqam: <b>{order.order_number}</b>",
        f"Mijoz: {full_name}",
        f"Telefon: {phone}",
        f"Status: {order.get_status_display() if hasattr(order, 'get_status_display') else 'Kutilmoqda'}",
        f"Umumiy mahsulotlar soni: {order.total_items}",
        f"Jami summa: {format_price(order.total_price)}",
        "",
        "Mahsulotlar tafsiloti:",
    ]
    try:
        items = list(order.items.select_related('product').all())
        if not items:
            lines.append("(Mahsulotlar topilmadi)")
        else:
            for idx, item in enumerate(items, start=1):
                unit = format_price(item.unit_price)
                total_line = format_price(item.total_price)
                name = item.product_name
                lines.append(f"{idx}. {name} — x{item.quantity} | {unit} => {total_line}")
            # Aggregated summary
            total_qty = sum(i.quantity for i in items)
            lines.append("")
            lines.append(f"Yig'indi: {total_qty} dona, {format_price(order.subtotal)}")
    except Exception as e:  # noqa
        lines.append(f"(Mahsulotlarni olishda xato: {e})")
    if order.delivery_address:
        lines.append("")
        lines.append(f"Manzil: {order.delivery_address[:180]}")
    if order.notes:
        lines.append(f"Izoh: {order.notes[:180]}")
    return '\n'.join(lines)


def build_customer_status_message(order: Order) -> str:
    base = [
        f"{CUSTOMER_HEADER_ICON} Buyurtma: {order.order_number}",
        STATUS_MESSAGES.get(order.status, "Holat yangilandi"),
        f"Holat: {order.get_status_display() if hasattr(order, 'get_status_display') else order.status}" ,
        f"Umumiy summa: {format_price(order.total_price)}",
    ]
    if order.status in ('pending', 'paid'):
        base.append(f"Mahsulotlar soni: {order.total_items}")
    return '\n'.join(base)


async def _send_messages_async(message_text: str, admins: Iterable[BotUser]):
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for admin in admins:
            payload = {
                'chat_id': admin.user_id,
                'text': message_text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': 'true'
            }
            try:
                async with session.post(API_URL, data=payload) as resp:
                    if resp.status == 403:
                        BotUser.objects.filter(pk=admin.pk).update(is_blocked=True)
                    elif resp.status == 429:  # Too Many Requests
                        try:
                            data = await resp.json()
                            retry_after = data.get('parameters', {}).get('retry_after', 3)
                        except Exception:
                            retry_after = 3
                        await asyncio.sleep(int(retry_after))
                        continue
                    elif resp.status >= 400:
                        text = await resp.text()
                        logger.warning(f"Telegram API error {resp.status}: {text}")
            except Exception as e:  # noqa
                logger.warning(f"Failed to send order notification to {admin.user_id}: {e}")


async def _send_single_chat(message_text: str, chat_id: str | int):
    timeout = aiohttp.ClientTimeout(total=8)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        payload = {
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': 'true'
        }
        try:
            async with session.post(API_URL, data=payload) as resp:
                if resp.status >= 400:
                    logger.warning(f"Telegram send error {resp.status} for chat {chat_id}")
        except Exception as e:  # noqa
            logger.warning(f"Telegram send exception for chat {chat_id}: {e}")


def notify_admins_new_order(order: Order):
    """Send Telegram notification to all bot admins about new order.
    Non-blocking: tries to schedule async sending on existing loop or runs its own loop.
    """
    try:
        admins = list(BotUser.objects.filter(is_admin=True, is_active=True, is_blocked=False).only('id', 'user_id'))
        if not admins:
            return
        message = build_order_message(order)
        # Run isolated event loop (short-lived)
        asyncio.run(_send_messages_async(message, admins))
    except Exception as e:  # noqa
        logger.error(f"notify_admins_new_order error: {e}")


def notify_customer_order_status(order: Order):
    """Send message to customer if phone_number linked to BotUser."""
    try:
        print("Order: ", order.contact_phone)
        if not order.contact_phone:
            return
        # Normalize phone for lookup (simple strip). Assume phone stored as raw.
        phone_variants = [order.contact_phone.strip(), order.contact_phone]
        # Try to match without + and spaces
        cleaned = order.contact_phone.replace('+', '').replace(' ', '').replace('-', '')
        phone_variants.append(cleaned)
        from apps.botapp.models import BotUser
        bot_user = BotUser.objects.filter(phone_number__in=phone_variants).order_by('-updated_at').first()
        if not bot_user:
            return
        message = build_customer_status_message(order)
        asyncio.run(_send_single_chat(message, bot_user.user_id))
    except Exception as e:  # noqa
        logger.error(f"notify_customer_order_status error: {e}")
