from aiogram import types
from loader import dp


@dp.message_handler(chat_type=['group', 'supergroup'])
async def byby(message: types.Message):
    await message.answer('Бот для работы в личном чате')
