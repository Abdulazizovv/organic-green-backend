from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from bot.loader import dp
from aiogram.dispatcher import FSMContext


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    """
    Handles the /start command.
    """
    await message.answer("Assalomu alaykum!")