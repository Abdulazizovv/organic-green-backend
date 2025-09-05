from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from bot.loader import dp
from aiogram.dispatcher import FSMContext
from apps.botapp.models import BotUser
from bot.keyboards.default import phone_request_kb
from asgiref.sync import sync_to_async


async def _update_or_create_bot_user(tg_user):
    return await sync_to_async(BotUser.objects.update_or_create)(
        user_id=str(tg_user.id),
        defaults={
            'first_name': tg_user.first_name or '',
            'last_name': tg_user.last_name or '',
            'username': tg_user.username or '',
            'language_code': tg_user.language_code or 'uz',
            'is_blocked': False,
            'is_active': True,
        }
    )


async def _save_phone(user_id: int, phone: str):
    return await sync_to_async(BotUser.objects.filter(user_id=str(user_id)).update)(phone_number=phone)


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    """Handles the /start command and registers user in DB."""
    await state.finish()
    tg_user = message.from_user
    obj, created = await _update_or_create_bot_user(tg_user)
    greeting = "Assalomu alaykum, botga xush kelibsiz!" if created else "Yana qaytganingizdan xursandmiz!"
    # Ask phone if not provided yet
    if not obj.phone_number:
        await message.answer(
            f"{greeting}\n\nRo'yxatdan o'tish uchun telefon raqamingizni yuboring.",
            reply_markup=phone_request_kb
        )
    else:
        await message.answer(f"{greeting}\nSiz avval ro'yxatdan o'tgansiz.")


@dp.message_handler(content_types=types.ContentType.CONTACT, state="*")
async def process_contact(message: types.Message, state: FSMContext):
    """Handle phone number submission from the user."""
    contact = message.contact
    if not contact or not contact.phone_number:
        return await message.answer("Telefon raqam topilmadi. Qaytadan urinib ko'ring.")
    # Ensure the contact belongs to the sender (security)
    if contact.user_id != message.from_user.id:
        return await message.answer("Faqat o'zingizning kontakt raqamingizni yuboring.")
    try:
        await _save_phone(message.from_user.id, contact.phone_number)
        await message.answer("Siz tizimda ro'yxatdan o'tdingiz ✅", reply_markup=types.ReplyKeyboardRemove())
    except Exception:
        await message.answer("Saqlashda xatolik yuz berdi. Keyinroq urinib ko'ring.")