from dataclasses import dataclass

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asyncpg import exceptions

from data.config import ADMINS
from filters.admin_filters import CallFilter
from utils.admin_menu_utils import create_menu_back, delete_all_after_time, \
    delete_loue_level_menu, create_level_menu, edit_message

from loader import dp
from utils.admin_utils import get_key_by_value
from utils.log import log
from work_vs_db.db_moderators import moderators_db
from work_vs_db.db_users import users_db


@dataclass()
class Data:
    options = {'access_to_buttons_tools': 'ab', 'access_to_files_tools': 'af', 'access_to_groups_tools': 'ag',
               'access_to_users_tools': 'au', 'access_to_state_tools': 'as'}

    opt_text = {'access_to_buttons_tools': 'Доступ к кнопкам', 'access_to_files_tools': 'Доступ к файлам',
                'access_to_groups_tools': 'Доступ к группам', 'access_to_users_tools': 'Доступ к пользователям',
                'access_to_state_tools': 'Доступ к монитрингу'}

    buttons_tools = {
        'name': 'n', 'group_buttons': 'gb', 'work_file': 'wf', 'size_blok': 'sb', 'num_block': 'nub',
        'name_block': 'nab', 'shablon_file': 'sf', 'active': 'a', 'sort': 's', 'hidden': 'h', 'users': 'u',
        'specification': 'sp', 'statistical': 'st', 'add_button': 'ad', 'del_button': 'db'}
    files_tools = {
        'num_line': 'n', 'change_file': 'af', 'del_file': 'df', 'add_new_file': 'nf', 'send_me_file': 'sf', 'instr': 'i'}
    groups_tools = {
        'name': 'n', 'users': 'u', 'hidden': 'h', 'specification': 's', 'del_group': 'dg', 'add_group_i': "ag"}
    users_tools = {
        'list_users': 'lu', 'add_user': 'au', 'del_user': 'du', 'reset_statistic': 'rs'}
    state_tools = {
        'buttons_groups': 'bg', 'buttons_files': 'bf', 'list_files': 'lf', 'list_users': 'lu', 'list_guests': 'lg',
        'statistic_today': 'st', 'statistic_all_tooday': 'sa'}


#  ----====  НАСТРОЙКА МОДЕРАТОРОВ  ====----
@dp.callback_query_handler(text="Настройка модераторов", state='*')
async def moders_menu(call: types.CallbackQuery, state: FSMContext):
    def moders_keyboard():
        settings_buttons = ['Список модераторов', 'Добавить модератора', 'Удалить модератора', 'Настройка прав доступа']
        keyb = InlineKeyboardMarkup(row_width=1)
        for butt in settings_buttons:
            inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
            keyb.add(inline_button)
        return keyb

    type_menu = 'id_msg_options'
    text = "Настройка модераторов:"
    chat_id = call.message.chat.id
    keyboard = moders_keyboard()

    await state.finish()
    await create_menu_back(call.message.chat.id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  ДОБАВИТЬ МОДЕРАТОРА  ====----
@dp.callback_query_handler(text="Добавить модератора", state='*')
async def add_moder(call: types.CallbackQuery, state: FSMContext):
    def add_moder_keyboard():
        users = users_db.users_id_names
        keyb = InlineKeyboardMarkup(row_width=1)
        text_keyb = 'сделать модератором '
        for user in users:
            if user not in moderators_db.moderators and user not in ADMINS:
                keyb.add(InlineKeyboardButton(text=text_keyb + users[user], callback_data=f'add_moder/{user}'))
        return keyb

    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    text = "Выберите нового модератора:"
    keyboard = add_moder_keyboard()

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.callback_query_handler(CallFilter(startswith='add_moder'), state='*')
async def add_moder_2(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    moder_id = int(query[1])
    user_name = users_db.users_id_names[moder_id]
    answer = f'Модератор {user_name} добавелен'

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        await moderators_db.write(moder_id, 'add_moderator', user_name)
    except exceptions.PostgresError:
        await create_level_menu(chat_id=chat_id, level=type_menu, text='Ошибка добавления модератора')
        await log.write(f'admin_menu: Ошибка добавления модератора, ({call.from_user.username})')
    else:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
        await log.write(f'admin_menu: {answer}, ({call.from_user.username})')
    finally:
        await call.answer()
        await delete_all_after_time(chat_id)


#  ----====  УДАЛИТЬ МОДЕРАТОРА  ====----
@dp.callback_query_handler(text='Удалить модератора', state='*')
async def moder_del(call: types.CallbackQuery, state: FSMContext):
    def del_moder_keyb():
        keyb = InlineKeyboardMarkup(row_width=1)
        for moder in moderators_db.moderators:
            user_name = users_db.users_id_names[moder]
            keyb.add(InlineKeyboardButton(text=f"Удалить {user_name}", callback_data=f'del_moder/{moder}'))
        return keyb

    type_menu = 'id_msg_tools'
    text = "Выберите модератора для удаления"
    chat_id = call.message.chat.id
    keyboard = del_moder_keyb()

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.callback_query_handler(CallFilter(startswith='del_moder'), state='*')
async def moder_del2(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    moder_id = int(query[1])
    user_name = users_db.users_id_names[moder_id]
    answer = f'Модератор {user_name} удален'

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        await moderators_db.write(moder_id, 'del_moderator')
    except exceptions.PostgresError:
        await create_level_menu(chat_id=chat_id, level=type_menu, text='Ошибка удаления модератора')
        await log.write(f'admin_menu: Ошибка удаления модератора, ({call.from_user.username})')
    else:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
        await log.write(f'admin_menu: {answer}, ({call.from_user.username})')
    finally:
        await call.answer()
        await delete_all_after_time(chat_id)


#  ----====  СПИСОК МОДЕРАТОРОВ  ====----
@dp.callback_query_handler(text="Список модераторов", state='*')
async def list_moderators(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    answer = await moderators_db.list_all_moderators()

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
    await call.answer()
    await log.write(f'admin_menu: список модераторов, ({call.from_user.username})')
    await delete_all_after_time(chat_id)


#  ----====  ВЫБОР МОДЕРАТОРА  ====----
@dp.callback_query_handler(text="Настройка прав доступа", state='*')
async def access_moder(call: types.CallbackQuery, state: FSMContext):
    def access_moder_keyb():
        keyb = InlineKeyboardMarkup(row_width=1)
        for moder in moderators_db.moderators:
            user_name = users_db.users_id_names[moder]
            keyb.add(InlineKeyboardButton(text=f"Настроить {user_name}", callback_data=f'acc_moder/{moder}'))
        return keyb

    type_menu = 'id_msg_options'
    chat_id = call.message.chat.id
    text = "Выберите модератора:"
    keyboard = access_moder_keyb()

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


#
#  ----====  ВЫБОР СВОЙСТВ  ====----
@dp.callback_query_handler(CallFilter(startswith='acc_moder'), state='*')
async def access_moder2(call: types.CallbackQuery, state: FSMContext):

    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    moder_id = int(query[1])
    user_name = users_db.users_id_names[moder_id]
    text = f'Настройка доступа модератора {user_name}'
    keyboard = options_moder_keyb(moder_id)

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.callback_query_handler(CallFilter(startswith='acc'), state='*')
async def access_moder2(call: types.CallbackQuery, state: FSMContext):

    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    moder_id = int(query[1])
    option_id = query[2]
    user_name = users_db.users_id_names[moder_id]
    text = f'Настройка доступа модератора {user_name}'
    keyboard = access_tools_keyb(moder_id, option_id)

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


#
#  ----====  УСТАНОВКА ПРАВ ДОСТУПА  ====----
@dp.callback_query_handler(CallFilter(startswith='set_acc'), state='*')
async def access_moder2(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_values'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    moder_id = int(query[1])
    option_id = query[2]
    access_id = query[3]

    options, acces, text = await set_access(option_id, access_id, moder_id)

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        print(moder_id, options, acces)
        await moderators_db.write(moder_id, options, acces)
    except exceptions.PostgresError:
        await create_level_menu(chat_id=chat_id, level=type_menu, text='Ошибка настройки доступа модератора')
        await log.write(f'admin_menu: Ошибка настройки доступа модератора, ({call.from_user.username})')
    else:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
        await log.write(f'admin_menu: {text}, ({call.from_user.username})')
        #  Обновление сообщения с tools
        if option_id != "all":
            await edit_message(chat_id=chat_id,
                               type_menu='id_msg_tools',
                               keyboard=(access_tools_keyb(moder_id, option_id)),
                               text=text)
        else:
            await edit_message(chat_id=chat_id,
                               type_menu='id_msg_tools',
                               keyboard=(options_moder_keyb(moder_id)),
                               text=text)
    finally:
        await call.answer()
        await delete_all_after_time(chat_id)


async def set_access(option_id, access_id, moder_id):

    def get_access(opt, access):
        moder_acc = getattr(moderators_db.moderators[moder_id], opt, None)
        all_tools = getattr(Data, opt[10:], None)
        acc__name = get_key_by_value(all_tools, access)
        tools, tools_id = get_tools(opt)
        acc_t = tools[acc__name]
        if moder_acc in ('None', None) or acc__name is None:
            return acc__name, "разрешен", acc_t
        elif moder_acc == 'all':
            acc = list(tools)
            acc.remove(acc__name)
            moder_acc = ",".join(acc)
            return moder_acc, "запрещен", acc_t
        elif acc__name in moder_acc.split(','):
            acc = moder_acc.split(',')
            acc.remove(acc__name)
            moder_acc = ",".join(acc)
            return moder_acc, "запрещен", acc_t
        else:
            acc = moder_acc.split(',')
            acc.append(acc__name)
            moder_acc = ",".join(acc)
            return moder_acc, "разрешен", acc_t

    moder_name = users_db.users_id_names[moder_id]

    if option_id == 'all':
        options = list(Data.options)
        option = 'Ошибка'
        opt_text = " доступ ко всему"
    else:
        option = get_key_by_value(Data.options, option_id)
        options = [option]
        opt_text = f" {Data.opt_text[option].lower()}"
    if access_id in ('all', 'None'):
        if access_id == 'all':
            acc_text = "разрешен любой"
        else:
            acc_text = "запрещен любой"
        acces = [access_id for i in range(len(options))]
        text = f'Модератору {moder_name} {acc_text}{opt_text}'
    else:
        new_acces, acc_text, acc_name = get_access(option, access_id)
        text = f'Модератору {moder_name} {acc_text} {opt_text} ({acc_name})'
        if new_acces:
            acces = [new_acces]
        else:
            acces = 'except'

    return options, acces, text


def get_tools(option):
    if option == 'access_to_buttons_tools':
        from .admin_menu_buttons import Data as ButtData
        tools = ButtData.button_tools
        tools.update({'add_button': 'Добавить кнопку', 'del_button': 'Удалить кнопку'})
        tools_id = Data.buttons_tools
        return tools, tools_id
    if option == 'access_to_groups_tools':
        from .admin_menu_groups import Data as GrData
        tools = GrData.group_tools
        tools.update({'add_group_i': 'Про добавление групп', 'del_group': 'Удалить группу'})
        tools_id = Data.groups_tools
        return tools, tools_id
    if option == 'access_to_files_tools':
        tools = {'num_line': '№ строки', 'change_file': 'Заменить файл', 'del_file': 'Удалить файл',
                 'add_new_file': 'Новый файл', 'send_me_file': 'Прислать файл', 'instr': 'Инструкция по загрузке'}
        tools_id = Data.files_tools
        return tools, tools_id
    if option == 'access_to_users_tools':
        tools = {'list_users': 'Список пользователей', 'add_user': 'Добавить пользователя',
                 'del_user': 'Удалить пользователя', 'reset_statistic': 'Сброс статистики'}
        tools_id = Data.users_tools
        return tools, tools_id
    if option == 'access_to_state_tools':
        tools = {'buttons_groups': 'Кнопки-группы', 'buttons_files': 'Кнопки-файлы', 'list_files': 'Список файлов',
                 'list_users': 'Список пользователей', 'list_guests': 'Список гостей',
                 'statistic_today': 'Статистика за сегодня', 'statistic_all_tooday': 'Вся статистика'}
        tools_id = Data.state_tools
        return tools, tools_id


def access_tools_keyb(moder_id, option_id):
    option = get_key_by_value(Data.options, option_id)
    tools, tools_id = get_tools(option)
    keyb = InlineKeyboardMarkup(row_width=1)
    for tool in tools:
        access = getattr(moderators_db.moderators[moder_id], option, None)
        if access and (access == 'all' or tool in access.split(',')):
            access = " - Да"
        else:
            access = " - Нет"
        keyb.add(InlineKeyboardButton(text=tools[tool] + access,
                                      callback_data=f'set_acc/{moder_id}/{option_id}/{tools_id[tool]}'))
    keyb.add(InlineKeyboardButton('Разрешить доступ ко всему', callback_data=f'set_acc/{moder_id}/{option_id}/all'))
    keyb.add(InlineKeyboardButton('Запретить доступ ко всему', callback_data=f'set_acc/{moder_id}/{option_id}/None'))
    return keyb


def options_moder_keyb(moder):
    opt_text = Data.opt_text
    keyb = InlineKeyboardMarkup(row_width=1)
    for option in Data.options:
        access = getattr(moderators_db.moderators[moder], option, None)
        if access == 'all':
            access = " - Полный"
        elif access is not None:
            access = " - Частичный"
        else:
            access = " - Нет"
        keyb.add(InlineKeyboardButton(text=opt_text[option] + access,
                                      callback_data=f'acc/{moder}/{Data.options[option]}'))
    keyb.add(InlineKeyboardButton(text='Разрешить доступ ко всему', callback_data=f'set_acc/{moder}/all/all'))
    keyb.add(InlineKeyboardButton(text='Запретить доступ ко всему', callback_data=f'set_acc/{moder}/all/None'))
    return keyb
