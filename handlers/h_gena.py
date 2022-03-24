from aiogram import types

from loader import dp
from utils.Proverka import prover
from utils.gena import gennadij
from utils.log import log


@dp.message_handler(commands=['gena'])
async def gena(message: types.Message):
    user = await prover(message, 'gena')  # проверяем статус пользователя и пишем статистику
    if user != "admin": return

    text = await gennadij.get_text()
    await message.answer(text)
    await log(f'admin: {message.text}, ({message.from_user.username})\n')
