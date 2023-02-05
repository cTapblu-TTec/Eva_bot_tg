from aiogram import types

from loader import dp
from utils.gena import gennadij
from utils.log import log


@dp.message_handler(commands=['gena'])
async def gena(message: types.Message):

    text = await gennadij.get_text()
    await message.answer(text)
    await log(f'admin: {message.text}, ({message.from_user.username})\n')
