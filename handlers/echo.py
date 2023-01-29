from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.face_control import control
from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def echo(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user == "guest": return

    echo_buttons = ['Волонтерство', 'Дополнительные функции']
    keyboard = InlineKeyboardMarkup(row_width=1)
    for butt in echo_buttons:
        inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
        keyboard.add(inline_button)
    await message.answer("Eva_bot:", reply_markup=keyboard)
