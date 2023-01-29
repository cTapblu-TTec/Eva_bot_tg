from loader import dp
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from utils.face_control import control
from work_vs_db.db_buttons import buttons_db


@dp.message_handler(CommandHelp())
async def description(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user == "guest": return

    text = 'Описание кнопок:\n'
    for button in buttons_db.buttons:
        if buttons_db.buttons[button].hidden == 0:
            text += f"• {buttons_db.buttons[button].name} - {buttons_db.buttons[button].specification}\n"

    if user == 'admin':
        text += '\nскрытые кнопки:\n'
        for button in buttons_db.buttons:
            if buttons_db.buttons[button].hidden == 1:
                text += f"• {buttons_db.buttons[button].name} - {buttons_db.buttons[button].specification}\n"

    await message.answer(text)
