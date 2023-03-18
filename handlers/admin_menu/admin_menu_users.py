from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from filters.admin_filters import CallFilter
from utils.admin_menu_utils import create_menu_back, delete_all_after_time, create_menu_cancel, \
    delete_loue_level_menu, create_level_menu

from loader import dp
from utils.face_control import Guests
from utils.log import log
from work_vs_db.db_moderators import moderators_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


class FCM(StatesGroup):
    waite_user_name = State()
    waite_delete_user = State()


tools = {'list_users': 'Список пользователей', 'add_user': 'Добавить пользователя',
         'del_user': 'Удалить пользователя', 'reset_statistic': 'Сброс статистики'}


async def users_keyboard(chat_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if await moderators_db.check_access_moderator(chat_id, 'access_to_users_tools', 'list_users'):
        keyboard.add(InlineKeyboardButton(text='Список пользователей', callback_data='all_users'))
    if await moderators_db.check_access_moderator(chat_id, 'access_to_users_tools', 'add_user'):
        keyboard.add(InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user'))
    if await moderators_db.check_access_moderator(chat_id, 'access_to_users_tools', 'del_user'):
        keyboard.add(InlineKeyboardButton(text='Удалить пользователя', callback_data='del_user'))
    if await moderators_db.check_access_moderator(chat_id, 'access_to_users_tools', 'reset_statistic'):
        keyboard.add(InlineKeyboardButton(text='Сброс статистики за сегодня', callback_data='clear_statistic'))
    return keyboard


async def guests_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    if Guests.guests:
        for guest_id in Guests.guests:
            keyboard.add(InlineKeyboardButton(
                text=f'добавить {guest_id} - {Guests.guests[guest_id]}',
                callback_data=f'add_guest/{guest_id}/{Guests.guests[guest_id]}'
            ))
    else:
        return None
    return keyboard


#  ----====  МЕНЮ ПОЛЬЗОВАТЕЛИ  ====----
@dp.callback_query_handler(text="Настройка пользователей", state='*')
async def users_menu(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_options'
    text = "Настройка пользователей:"
    chat_id = call.message.chat.id
    keyboard = await users_keyboard(chat_id)

    await state.finish()
    await create_menu_back(call.message.chat.id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ  ====----
@dp.callback_query_handler(text="add_user", state='*')
async def users_add_user(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    keyboard = await guests_keyboard()
    text1 = "Введите имя нового пользователя"
    text2 = " или выберите из гостей:"

    await state.finish()
    await create_menu_cancel(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    if keyboard:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=text1+text2, keyboard=keyboard)
    else:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=text1)
    await state.set_state(FCM.waite_user_name.state)
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.callback_query_handler(CallFilter(startswith='add_guest'), state=FCM.waite_user_name)
async def users_add_user_2(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    user_name = query[2]

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    if user_name:
        new_user = user_name
        answer = await users_db.add_user(new_user)
        # удалить из гостей
        Guests.guests.pop(int(query[1]))
        await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
        await log.write(f'admin_menu: {answer}, ({call.from_user.username})')
    else:
        await create_level_menu(chat_id=chat_id, level=type_menu, text='У пользователя должно быть @user_name')
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.message_handler(state=FCM.waite_user_name)
async def users_add_user_2(message: types.Message, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = message.chat.id
    new_user = message.text
    answer = await users_db.add_user(new_user)

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=message.chat.id, type_menu='id_msg_tools')
    await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
    await log.write(f'admin_menu: {answer}, ({message.from_user.username})')
    await delete_all_after_time(chat_id)


#  ----====  УДАЛИТЬ ПОЛЬЗОВАТЕЛЯ  ====----
@dp.callback_query_handler(text='del_user', state='*')
async def users_del_user(call: types.CallbackQuery, state: FSMContext):
    def del_user_keyb():
        all_users = users_db.users_names
        keyb = InlineKeyboardMarkup(row_width=1)
        for user in all_users:
            keyb.add(InlineKeyboardButton(text=f"Удалить {user}", callback_data=f'del_user/{user}'))
        keyb.add(InlineKeyboardButton(text='Отмена', callback_data='Отмена'))
        return keyb

    type_menu = 'id_msg_tools'
    text = "Выберите пользователя для удаления"
    chat_id = call.message.chat.id
    keyboard = del_user_keyb()

    await state.finish()
    await create_menu_cancel(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await state.set_state(FCM.waite_delete_user.state)
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.callback_query_handler(CallFilter(startswith='del_user'), state=FCM.waite_delete_user)
async def users_del_user_2(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    user = query[1]
    answer = await users_db.del_user(user)

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
    await log.write(f'admin_menu: {answer}, ({call.from_user.username})')
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  СПИСОК ПОЛЬЗОВАТЕЛЕЙ  ====----
@dp.callback_query_handler(text="all_users", state='*')
async def users_all_users(call: types.CallbackQuery, state: FSMContext):
    def list_all_users():
        users_names = users_db.users_names
        num = len(users_names)
        users_names.sort(key=str.lower)
        users = "\n".join(users_names)
        return f'Всего {num} пользователей:\n{users}'

    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    answer = list_all_users()

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
    await call.answer()
    await log.write(f'admin_menu: список пользователей, ({call.from_user.username})')
    await delete_all_after_time(chat_id)


#  ----====  СБРОС СТАТИСТИКИ ЗА СЕГОДНЯ  ====----
@dp.callback_query_handler(text="clear_statistic", state='*')
async def users_clear_statistic(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    answer = "Cтатистика за сегодня сброшена"

    await state.finish()
    await create_menu_back(chat_id)
    await stat_db.dell()
    await stat_db.create(None)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
    await call.answer()
    await log.write(f'admin_menu: сброс статистики за сегодня, ({call.from_user.username})')
    await delete_all_after_time(chat_id)
