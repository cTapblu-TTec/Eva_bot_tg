from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import ADMINS
from filters.users_filters import FilterForStart, CallFilterForError
from loader import dp
from utils.admin_menu_utils import create_menu_back, delete_last_menu
from utils.log import log
from work_vs_db.db_groups_buttons import groups_db


async def keyboard_groups(user, is_admin):
    not_hidden_groups = []
    hidden_groups = []
    for group in groups_db.groups:
        if groups_db.groups[group].hidden == 0:
            not_hidden_groups.append(group)
        elif (groups_db.groups[group].users and user in groups_db.groups[group].users) or is_admin:
            hidden_groups.append(group)

    keyboard = InlineKeyboardMarkup(row_width=1)
    for group in (not_hidden_groups + hidden_groups):
        keyboard.add(InlineKeyboardButton(text=f'{group} - {groups_db.groups[group].specification}\n',
                                          callback_data=('menu_groups/' + group)))
    return keyboard


# все сообщения от пользователей
@dp.message_handler(FilterForStart(), state="*", content_types=[types.ContentType.ANY])
async def start(message: types.Message):
    username = message.from_user.username
    is_admin = message.chat.id in ADMINS
    keyboard = await keyboard_groups(username, is_admin)
    await message.answer("Группы кнопок для волонтерства:", reply_markup=keyboard)


# Эхо хендлер, куда летят не обработанные калбеки (ошибки) пользователей
@dp.callback_query_handler(CallFilterForError(), state='*')
async def errors_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer(f"Отменено")
    if call.data != "Отмена":
        await log.write(f"Ошибка кнопок, call.data: '{call.data}' ({call.from_user.username})", 'admin')
    await call.answer()


# первый хендлер для админов
@dp.message_handler(text='Отмена', state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    await delete_last_menu(message.chat.id)
