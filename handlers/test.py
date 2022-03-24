from aiogram import types

from data.config import ADMINS
from loader import dp


@dp.message_handler(commands=['test'])
async def ad_rs(message: types.Message):

    if str(message.from_user.id) in ADMINS:
        print('test')
