from aiogram import types

from data.config import ADMINS
from filters.users_filters import FilterForBattonsMenu, CallFilterForBattonsMenu
from loader import dp
from utils.admin_menu_utils import delete_loue_level_menu
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_moderators import moderators_db
from work_vs_db.db_users import users_db


async def group_button_list(group, username, admin):
    button_list = []
    for button in buttons_db.buttons:
        if buttons_db.buttons[button].active == 1 and buttons_db.buttons[button].group_buttons:
            # создаем список групп если кнопка состоит не в одной группе
            list_grups = ''
            if ',' in buttons_db.buttons[button].group_buttons:
                list_grups = buttons_db.buttons[button].group_buttons
                list_grups = list_grups.replace(' ', '')
                list_grups = list_grups.split(',')

            if buttons_db.buttons[button].group_buttons == group or group in list_grups:
                # админ todo скрытые кнопки для модераторов показывать? - наверно нет
                if admin:
                    button_list.append(button)
                # кнопка не скрыта (список юзеров пуст)
                elif buttons_db.buttons[button].hidden == 0 and buttons_db.buttons[button].users is None:
                    button_list.append(button)
                # юзер в списке кнопки
                elif buttons_db.buttons[button].users is not None and \
                        username in buttons_db.buttons[button].users:
                    button_list.append(button)
    if not button_list: button_list = ['Выбор группы кнопок']
    return button_list


async def menu_keyboard(button_list, admin, user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if admin:
        keyboard.add(*['Мои настройки', 'Админка', 'Мониторинг'])

    elif user_id in moderators_db.moderators:
        access_settings = await moderators_db.check_access_moderator(
            user_id, ['access_to_buttons_tools', 'access_to_files_tools', 'access_to_groups_tools',
                      'access_to_users_tools'])
        access_state = await moderators_db.check_access_moderator(user_id, 'access_to_state_tools', 'any')
        moder_menu = ['Мои настройки']
        if access_settings:
            moder_menu.append('Админка')
        if access_state:
            moder_menu.append('Мониторинг')
        if len(moder_menu) < 3:
            moder_menu.append('Выбор группы кнопок')
        keyboard.add(*moder_menu)

    else:
        keyboard.add(*['Мои настройки', 'Выбор группы кнопок'])

    # добавляем кнопки группы
    buttons = []
    for button in button_list:
        buttons.append(button)
        if len(buttons) % 2 == 0:
            keyboard.add(*buttons)
            buttons = []
    if buttons:
        keyboard.add(*buttons)
    return keyboard


# СОЗДАНИЕ НУЖНОГО  МЕНЮ
# по кнопке "Назад" - прилетает сюда
@dp.message_handler(FilterForBattonsMenu())
async def create_buttons(message: types.Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    group = message.text
    if group == 'Назад' and users_db.users[user_name].menu:
        group = users_db.users[user_name].menu
    is_admin = message.chat.id in ADMINS
    is_moder = message.chat.id in moderators_db.moderators
    button_list = await group_button_list(group, user_name, is_admin)
    keyboard = await menu_keyboard(button_list, is_admin, user_id)
    text_message = "создана группа кнопок '" + group + "'"

    if is_admin or is_moder:
        await adm_chats_db.write(chat_id=message.chat.id, tools=['menu_back', 'menu_cancel'], values=['false', 'false'])
        await delete_loue_level_menu(message.chat.id, 'id_msg_settings')
    await message.answer(text_message, reply_markup=keyboard)
    await users_db.write(user_name, ['menu', 'user_id'], [group, user_id])
    users_db.users[user_name].menu = group
    users_db.users[user_name].user_id = user_id


# создаем список кнопок из нужной группы - выбор группы в инлайн меню
@dp.callback_query_handler(CallFilterForBattonsMenu())
async def create_buttons_2(call: types.CallbackQuery):
    query = call.data.split('/')
    group = query[1]
    is_admin = call.message.chat.id in ADMINS
    user_name = call.from_user.username
    user_id = call.from_user.id
    button_list = await group_button_list(group, user_name, is_admin)
    keyboard = await menu_keyboard(button_list, is_admin, user_id)
    text_message = "создана группа кнопок '" + group + "'"

    if is_admin:
        text_message += "\nКнопки 'Админка' и 'Мониторинг' видны только админам и модераторам"
        await adm_chats_db.write(chat_id=user_id, tools=['menu_back', 'menu_cancel'], values=['false', 'false'])
        await delete_loue_level_menu(user_id, 'id_msg_settings')

    await call.message.answer(text_message, reply_markup=keyboard)
    await users_db.write(user_name, ['menu', 'user_id'], [group, user_id])
    users_db.users[user_name].menu = group
    users_db.users[user_name].user_id = user_id
    await call.answer()


@dp.message_handler(commands=['del'])
async def delete_buttons(message: types.Message):
    await message.answer('клавиатура удалена', reply_markup=types.ReplyKeyboardRemove())
