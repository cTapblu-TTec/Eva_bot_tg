from aiogram import types

from filters.chek_buttons import ChekGroupButtons
from utils.face_control import control
from loader import dp
from work_vs_db.db_buttons import buttons_db


@dp.message_handler(ChekGroupButtons())
async def create_buttons(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user == "guest": return

    # создаем список кнопок из нужной группы
    button_list = []
    for button in buttons_db.buttons:
        # создаем список групп если кнопка состоит не в одной группе
        list_grups = ''
        if ',' in buttons_db.buttons[button].group_buttons:
            list_grups = buttons_db.buttons[button].group_buttons
            list_grups = list_grups.replace(' ', '')
            list_grups = list_grups.split(',')

        if buttons_db.buttons[button].group_buttons == message.text or message.text in list_grups:
            # админ
            if user == 'admin':
                button_list.append(button)
            # кнопка не скрыта, список юзеров пуст
            elif buttons_db.buttons[button].hidden == 0 and buttons_db.buttons[button].users is None:
                button_list.append(button)
            # юзер в списке кнопки
            elif buttons_db.buttons[button].users is not None and \
                    message.from_user.username in buttons_db.buttons[button].users:
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
