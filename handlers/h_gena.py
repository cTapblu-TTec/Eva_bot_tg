from aiogram import types

from loader import dp
from utils.face_control import control
from utils.gena import gennadij
from utils.log import log


@dp.message_handler(commands=['gena'])
async def gena(message: types.Message):
    user = await control(message)  # проверяем статус пользователя и пишем статистику
    if user != "admin": return

    text = await gennadij.get_text()
    await message.answer(text)
    await log(f'admin: {message.text}, ({message.from_user.username})\n')
