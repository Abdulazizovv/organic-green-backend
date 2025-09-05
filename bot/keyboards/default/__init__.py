from .category import home

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Registration keyboard for requesting phone number
phone_request_kb = ReplyKeyboardMarkup(resize_keyboard=True)
phone_request_kb.add(KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True))