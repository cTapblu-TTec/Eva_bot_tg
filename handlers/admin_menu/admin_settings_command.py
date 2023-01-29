from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.admin_menu_utils import dellete_old_message, delete_all_after_time
from loader import dp
from utils.face_control import control
from work_vs_db.db_adm_chats import adm_chats_db


@dp.message_handler(commands='settings', state='*')
async def settings_button(message: types.Message, state: FSMContext):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    await state.finish()
    await dellete_old_message(message.chat.id, 'id_msg_settings')

    settings_buttons = ['Настройка кнопок', 'Настройка файлов', 'Настройка групп', 'Настройка пользователей']
    keyboard = InlineKeyboardMarkup(row_width=1)
    for butt in settings_buttons:
        inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
        keyboard.add(inline_button)
    msg = await message.answer("Настройки бота:", reply_markup=keyboard)
    await adm_chats_db.write(chat_id=message.chat.id, tools=['id_msg_settings'], values=[msg["message_id"]])

    await dellete_old_message(message.chat.id, 'id_msg_options')
    await dellete_old_message(message.chat.id, 'id_msg_tools')
    await dellete_old_message(message.chat.id, 'id_msg_values')

    #  авто удаление через 30 мин
    await delete_all_after_time(message.chat.id)