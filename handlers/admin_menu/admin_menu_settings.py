from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.admin_menu_utils import delete_all_after_time, create_menu_back, delete_loue_level_menu, create_level_menu
from loader import dp
from work_vs_db.db_moderators import moderators_db


@dp.message_handler(text='Админка', state='*')
async def start_menu(message: types.Message, state: FSMContext):
    async def start_menu_keyboard():
        settings_buttons = {'Настройка кнопок': 'access_to_buttons_tools',
                            'Настройка файлов': 'access_to_files_tools',
                            'Настройка групп': 'access_to_groups_tools',
                            'Настройка пользователей': 'access_to_users_tools',
                            'Настройка модераторов': None}
        keyb = InlineKeyboardMarkup(row_width=1)
        for butt in settings_buttons:
            if await moderators_db.check_access_moderator(chat_id, settings_buttons[butt], 'any'):
                keyb.add(InlineKeyboardButton(text=butt, callback_data=butt))
        return keyb

    type_menu = 'id_msg_settings'
    text = "Настройки бота:"
    chat_id = message.chat.id
    keyboard = await start_menu_keyboard()

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    #  авто удаление через 30 мин
    await delete_all_after_time(chat_id)
