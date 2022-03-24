from aiogram import types

from utils.Proverka import prover
from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    user = await prover(message, 'other')  # проверяем статус пользователя
    if user == "guest": return

    text_message = "для кнопок инсты введи - i\n" \
                   "для кнопок ВК, введи - v\n"
    if user == 'admin':
        text_message += "\n/admin - админские команды\n" \
                        "д - Дашины кнопки"
    await message.answer(text_message)
