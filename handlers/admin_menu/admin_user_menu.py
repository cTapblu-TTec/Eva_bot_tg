from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.admin_menu_utils import dellete_old_message, create_menu_back, delete_all_after_time, create_menu_cancel

from loader import dp
from utils.admin_utils import add_user, del_user
from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


class FCM(StatesGroup):
    waite_user_name = State()
    waite_delete_user = State()


async def users_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Список пользователей', callback_data='all_users'))
    keyboard.add(InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user'))
    keyboard.add(InlineKeyboardButton(text='Удалить пользователя', callback_data='del_user'))
    keyboard.add(InlineKeyboardButton(text='Статистика за сегодня', callback_data='tooday_statistic'))
    keyboard.add(InlineKeyboardButton(text='Сброс статистики за сегодня', callback_data='clear_statistic'))
    return keyboard


#  ----====  ВЫБОР ГРУППЫ  ====----
@dp.callback_query_handler(text="Настройка пользователей", state='*')
async def settings_users(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_options')
    # id_msg_options
    keyboard = await users_keyboard()
    msg = await call.message.answer("Настройка пользователей:", reply_markup=keyboard)

    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_options'], values=[msg["message_id"]])
    await call.answer()
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    await delete_all_after_time(call.message.chat.id)


#  ----====  ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ  ====----
@dp.callback_query_handler(text="add_user", state='*')
async def users_add_user(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    await call.message.answer("Введите имя пользователя")
    await state.set_state(FCM.waite_user_name.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


@dp.message_handler(state=FCM.waite_user_name)
async def users_add_user_2(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    new_user = message.text
    all_users = users_db.users_names
    answer = await add_user(new_user, all_users)
    await message.answer(answer)
    await log.write(f'admin_menu: {answer}, ({message.from_user.username})')


#  ----====  УДАЛИТЬ ПОЛЬЗОВАТЕЛЯ  ====----
@dp.callback_query_handler(text='del_user', state='*')
async def users_del_user(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')

    all_users = users_db.users_names
    keyboard = InlineKeyboardMarkup(row_width=1)
    for user in all_users:
        keyboard.add(InlineKeyboardButton(text=f"Удалить {user}", callback_data=user))
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='Отмена'))
    msg = await call.message.answer("Выберите пользователя для удаления", reply_markup=keyboard)

    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_tools'], values=[msg["message_id"]])
    await state.set_state(FCM.waite_delete_user.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


# Если вместо кнопки удаления пользователь что-то ввел
@dp.message_handler(state=FCM.waite_delete_user)
async def users_del_user_2_mess(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    await dellete_old_message(chat_id=message.chat.id, type_menu='id_msg_tools')


@dp.callback_query_handler(state=FCM.waite_delete_user)
async def users_del_user_2(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    if call.data == 'Отмена':
        return

    new_user = call.data
    all_users = users_db.users_names
    answer = await del_user(new_user, all_users)
    await call.message.answer(answer)
    await log.write(f'admin_menu: {answer}, ({call.message.chat.username})')


#  ----====  СПИСОК ПОЛЬЗОВАТЕЛЕЙ  ====----
@dp.callback_query_handler(text="all_users", state='*')
async def users_all_users(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)

    users_names = users_db.users_names
    num = len(users_names)
    users_names.sort(key=str.lower)
    users = "\n".join(users_names)
    await call.message.answer(f'Всего {num} пользователей:\n{users}')
    await call.answer()
    await delete_all_after_time(call.message.chat.id)
    await log.write(f'admin_menu: список пользователей, ({call.message.chat.username})')


#  ----====  СТАТИСТИКА ЗА СЕГОДНЯ  ====----
@dp.callback_query_handler(text="tooday_statistic", state='*')
async def users_tooday_statistic(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await stat_db.get_html()
    with open('statistic.html', 'rb') as file:
        await call.message.answer_document(file)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)
    await log.write(f'admin_menu: статистика за сегодня, ({call.message.chat.username})')


#  ----====  СБРОС СТАТИСТИКИ ЗА СЕГОДНЯ  ====----
@dp.callback_query_handler(text="clear_statistic", state='*')
async def users_clear_statistic(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await stat_db.dell()
    await stat_db.create(None)
    await call.message.answer("Cтатистика за сегодня сброшена")
    await call.answer()
    await delete_all_after_time(call.message.chat.id)
    await log.write(f'admin_menu: сброс статистики за сегодня, ({call.message.chat.username})')
