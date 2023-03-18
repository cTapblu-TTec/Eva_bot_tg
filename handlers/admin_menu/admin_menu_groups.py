from dataclasses import dataclass
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from asyncpg import exceptions as asyncpg_ex

from filters.admin_filters import CallFilter
from utils.admin_menu_utils import create_menu_back, create_menu_cancel, edit_message, \
    delete_all_after_time, delete_loue_level_menu, create_level_menu
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp
from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_moderators import moderators_db
from work_vs_db.manager_bd import delete_group, change_group_tool


@dataclass()
class Data:
    group_tools = {
        'name': 'Имя группы',
        'hidden': 'Скрытая группа (1/0)',
        'users': 'Кому доступ скрытой',
        'specification': 'Описание',
    }


class FCM(StatesGroup):
    waite_tool_group = State()
    waite_value_group = State()


async def groups_keyboard(chat_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for group in groups_db.groups:
        keyboard.add(InlineKeyboardButton(text=f'Настройка группы "{group}"', callback_data='g_tool/' + group))
    if await moderators_db.check_access_moderator(chat_id, 'access_to_groups_tools', 'add_group_i'):
        keyboard.add(InlineKeyboardButton(text='Про добавление групп', callback_data='add_group_i'))
    return keyboard


async def tools_gr_keyboard(group, chat_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for tool in Data.group_tools:
        if await moderators_db.check_access_moderator(chat_id, 'access_to_groups_tools', tool):
            value = getattr(groups_db.groups[group], tool, None)
            tool_text = Data.group_tools[tool]
            c_data = f'gr_value/{group}/{tool}'
            inline_button = InlineKeyboardButton(text=f'{tool_text} --==-- {value}', callback_data=c_data)
            keyboard.add(inline_button)
    if await moderators_db.check_access_moderator(chat_id, 'access_to_groups_tools', 'del_group'):
        keyboard.add(InlineKeyboardButton(text='Удалить группу', callback_data='del_group/' + group))
    return keyboard


#  ----====  ВЫБОР ГРУППЫ  ====----
@dp.callback_query_handler(text="Настройка групп", state='*')
async def groups_menu(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_options'
    chat_id = call.message.chat.id
    text = "Настройка групп кнопок:"
    keyboard = await groups_keyboard(chat_id)

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  ПРО ДОБАВЛЕНИЕ ГРУПП ====----
@dp.callback_query_handler(text='add_group_i', state='*')
async def add_group(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    text = "Группы добавляются автоматически, когда вносятся в 'Меню кнопок' настроек кнопки. "\
           "Кнопку можно добавить в несколько групп, указав их в 'Меню кнопок' через запятые."

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  УДАЛИТЬ ГРУППУ ====----
@dp.callback_query_handler(CallFilter(startswith='del_group'), state='*')
async def del_group(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    group = call.data.split('/')[1]
    text = f"Группа {group} удалена"

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)

    try:
        await delete_group(group)
    except asyncpg_ex.PostgresError:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=f"Группа {group} не удалена")
        await log.write(f"admin_menu: Группа {group} не удалена ({call.from_user.username})")
    else:
        await edit_message(chat_id=chat_id,
                           type_menu='id_msg_options',
                           keyboard=(await groups_keyboard(chat_id)),
                           text=f"Группа {group} удалена")
        await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
        await log.write(f"admin_menu: Группа {group} удалена ({call.from_user.username})")
    finally:
        await call.answer()
        await delete_all_after_time(chat_id)


#  ----====  ВЫБОР ПАРАМЕТРА ГРУППЫ  ====----
@dp.callback_query_handler(CallFilter(startswith='g_tool'), state="*")
async def group_tool_menu(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    group = query[1]
    keyboard = await tools_gr_keyboard(group, chat_id)
    text = f"Выберите параметр группы '{group}' для настройки:"

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====----
@dp.callback_query_handler(CallFilter(startswith='gr_value'))
async def group_ask_value(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_values'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    group = query[1]
    tool = query[2]
    tool_text = Data.group_tools[tool]
    text = f"Введите значение параметра '{tool_text}' для группы '{group}'"

    await state.finish()
    await create_menu_cancel(chat_id)
    await adm_chats_db.write(chat_id=chat_id, tools=['option', 'tool'], values=[group, tool])
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
    await state.set_state(FCM.waite_value_group.state)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_value_group)
async def group_read_value(message: types.Message, state: FSMContext):
    type_menu = 'id_msg_values'
    chat_id = message.chat.id
    group = adm_chats_db.chats[chat_id].option
    tool = adm_chats_db.chats[chat_id].tool
    value = message.text
    tool_text = Data.group_tools[tool]
    text = f"Значение '{value}' параметра '{tool_text}' для группы '{group}' установлено."

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        await change_group_tool(group, tool, value)
    except asyncpg_ex.PostgresError:
        ans = f"Значение '{value}' параметра '{tool_text}' для группы '{group}' не установлено!"
        await create_level_menu(chat_id=chat_id, level=type_menu, text=ans)
        await log.write(f"admin_menu: {ans} ({message.from_user.username})")
    else:
        if tool == "name":
            group_name = value
            await edit_message(chat_id=chat_id,
                               type_menu='id_msg_options',
                               keyboard=(await groups_keyboard(chat_id)),
                               text=f"Группа {group} переименована")
        else:
            group_name = group
        #  Обновление сообщения с tools
        await edit_message(chat_id=chat_id,
                           type_menu='id_msg_tools',
                           keyboard=(await tools_gr_keyboard(group_name, chat_id)),
                           text=text)
        await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
        await log.write(f"admin_menu: {text} ({message.from_user.username})")
    finally:
        await delete_all_after_time(chat_id)
