from aiogram import types

from utils.Proverka import prover
from loader import dp
from work_vs_db.db_buttons import buttons_db


@dp.message_handler(text=buttons_db.buttons_groups)
async def create_buttons(message: types.Message):
    user = await prover(message, 'other')  # проверяем статус пользователя
    if user == "guest": return

    # создаем список кнопок из нужной группы
    button_list = []
    for button in buttons_db.buttons:
        if buttons_db.buttons[button].group_buttons == message.text:
            button_list.append(button)

    # добавляем админские кнопки
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user == 'admin':
        buttons = ['/admin', '/st', '/stUsers']
        keyboard.add(*buttons)

    if message.from_user.username == 'dariasuv':
        buttons = '/st'
        keyboard.add(buttons)

    # добавляем кнопки группы
    buttons = []
    for button in button_list:
        buttons.append(button)
        if len(buttons) % 2 == 0:
            keyboard.add(*buttons)
            buttons = []
    if buttons:
        keyboard.add(*buttons)

    text_message = "создана группа кнопок '" + message.text + "'"
    if user == 'admin':
        text_message += "\n/admin - админские команды"
    await message.answer(text_message, reply_markup=keyboard)
