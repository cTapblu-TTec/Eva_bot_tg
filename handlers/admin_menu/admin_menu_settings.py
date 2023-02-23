from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.admin_menu_utils import delete_all_after_time, create_menu_back, delete_loue_level_menu, create_level_menu
from loader import dp


@dp.message_handler(commands='settings', state='*')
async def start_menu(message: types.Message, state: FSMContext):
    def start_menu_keyboard():
        settings_buttons = ['Настройка кнопок', 'Настройка файлов', 'Настройка групп', 'Настройка пользователей']
        keyboard = InlineKeyboardMarkup(row_width=1)
        for butt in settings_buttons:
            inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
            keyboard.add(inline_button)
        return keyboard

    type_menu = 'id_msg_settings'
    text = "Настройки бота:"
    chat_id = message.chat.id

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=start_menu_keyboard())
    #  авто удаление через 30 мин
    await delete_all_after_time(chat_id)
