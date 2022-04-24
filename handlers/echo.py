from aiogram import types

from utils.face_control import control
from loader import dp

from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def echo(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user == "guest": return

    text_message = 'Для создания кнопок введи:\n'
    for group in buttons_db.buttons_groups:
        if groups_db.groups[group].hidden == 0:
            text_message += f'"{group}" - {groups_db.groups[group].specification}\n'
        else:  # скрытые группы для допущенных
            if groups_db.groups[group].users and message.from_user.username in groups_db.groups[group].users:
                text_message += f'"{group}" - {groups_db.groups[group].specification}\n'

    if user == 'admin':
        text_message += "\n/admin - админские команды\n"
        for group in buttons_db.buttons_groups:
            if groups_db.groups[group].hidden == 1:
                text_message += f'"{group}" - {groups_db.groups[group].specification}\n'

    text_message += '\nОписание кнопок - /help'

    await message.answer(text_message)
