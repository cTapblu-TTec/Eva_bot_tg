from aiogram import types

from data.config import ADMINS
from loader import dp


@dp.message_handler(commands=['test'])
async def test(message: types.Message):

    if message.from_user.id in ADMINS:
        print('test')
