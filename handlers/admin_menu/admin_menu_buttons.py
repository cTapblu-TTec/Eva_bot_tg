from dataclasses import dataclass

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from asyncpg import exceptions

from filters.admin_filters import CallFilterForButtonValueFile, CallFilter
from loader import dp
from utils.admin_utils import get_button_clicks
from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from utils.admin_menu_utils import create_menu_back, create_menu_cancel, edit_message, \
    delete_all_after_time, delete_loue_level_menu, create_level_menu
from work_vs_db.db_moderators import moderators_db
from work_vs_db.manager_bd import add_button, del_button, change_button_tool


@dataclass()
class Data:
    buttons = {}
    button_tools = {
        'name': 'Имя кнопки',
        'group_buttons': 'Меню кнопок',
        'work_file': 'Файл отметок',
        'size_blok': 'кол-во отметок',
        'num_block': '№ блока',
        'name_block': 'Текст после №',
        'shablon_file': 'Файл шаблона',
        'active': 'Вкл/Выкл (1/0)',
        'sort': 'Порядок в меню',
        'hidden': 'Скрытая кнопка (1/0)',
        'users': 'Кому доступ скрытой',
        'specification': 'Описание',
        'statistical': 'Учитывать в статистике (1/0)',
    }


class FCM(StatesGroup):
    waite_butt_value = State()
    waite_set_file = State()


async def buttons_keyboard(chat_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = buttons_db.buttons
    for butt in buttons:
        cliks = await get_button_clicks(butt)
        button_cliks = ''
        if cliks:
            button_cliks = f' - {cliks}'
        callback_data = 'b_tool/' + buttons_db.buttons[butt].num_button
        keyboard.add(InlineKeyboardButton(text=f'{butt}{button_cliks}', callback_data=callback_data))
    access = await moderators_db.check_access_moderator(chat_id, 'access_to_buttons_tools', 'add_button')
    if access:
        keyboard.add(InlineKeyboardButton(text='Добавить кнопку', callback_data='add_button'))
    return keyboard


async def button_tools_keyboard(button, num_butt, chat_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for tool in Data.button_tools:
        access = await moderators_db.check_access_moderator(chat_id, 'access_to_buttons_tools', tool)
        if access:
            value = getattr(buttons_db.buttons[button], tool, None)
            tool_text = Data.button_tools[tool]
            inline_button = InlineKeyboardButton(text=f'{tool_text} --==-- {value}',
                                                 callback_data=f'bt_value/{num_butt}/{tool}')
            keyboard.add(inline_button)
    access = await moderators_db.check_access_moderator(chat_id, 'access_to_buttons_tools', 'del_button')
    if access:
        keyboard.add(InlineKeyboardButton(text='Удалить кнопку', callback_data='del_button/' + num_butt))
    return keyboard


# ____________________________________ask_options____________________________________
#  ----====  ВЫБОР КНОПКИ ====----
@dp.callback_query_handler(text="Настройка кнопок", state='*')
async def buttons_menu(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_options'
    text = "Настройка кнопок"
    chat_id = call.message.chat.id
    keyboard = await buttons_keyboard(chat_id)

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


# ____________________________________ask_tools____________________________________
#  ----====  ДОБАВИТЬ КНОПКУ ====----
@dp.callback_query_handler(text='add_button', state='*')
async def add_button_h(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id

    await state.finish()
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)

    if 'Новая кнопка' not in buttons_db.buttons:
        try:
            await add_button('Новая кнопка')
        except exceptions.PostgresError:
            await create_level_menu(chat_id=chat_id, level=type_menu, text='Не удалось добавить кнопку')
            await log.write(f"admin_menu: Не удалось добавить кнопку ({call.from_user.username})")
        else:
            await edit_message(chat_id=chat_id,
                               type_menu='id_msg_options',
                               keyboard=await buttons_keyboard(chat_id),
                               text="Кнопка 'Новая кнопка' добавлена")
            text = "Кнопка 'Новая кнопка' добавлена, можете ее переименовать"
            await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
            await log.write(f"admin_menu: Кнопка добавлена ({call.from_user.username})")
    else:
        text = "Кнопка 'Новая кнопка' уже есть, можете ее переименовать"
        await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  ВЫБОР ПАРАМЕТРА КНОПКИ  ====----
@dp.callback_query_handler(CallFilter(startswith='b_tool'), state="*")
async def button_tools(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    num_butt = query[1]
    button = buttons_db.button_numbers[num_butt]
    keyboard = await button_tools_keyboard(button, num_butt, chat_id)
    text = f"Настройка кнопки '{button}'"

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  УДАЛИТЬ КНОПКУ ====----
@dp.callback_query_handler(CallFilter(startswith='del_button'), state='*')
async def del_button_h(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    num_butt = query[1]
    button = buttons_db.button_numbers[num_butt]

    await state.finish()
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)

    try:
        await del_button(button)
    except exceptions.PostgresError:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=f"Не удалось удалить кнопку {button}")
        await log.write(f"admin_menu: Не удалось удалить кнопку {button} ({call.from_user.username})")
    else:
        await edit_message(chat_id=chat_id,
                           type_menu='id_msg_options',
                           keyboard=(await buttons_keyboard(chat_id)),
                           text=f"Кнопка {button} удалена")
        await create_level_menu(chat_id=chat_id, level=type_menu, text=f"Кнопка {button} удалена")
        await log.write(f"admin_menu: Кнопка {button} удалена ({call.from_user.username})")
    finally:
        await call.answer()
        await delete_all_after_time(chat_id)


# ____________________________________ask_values____________________________________
#  ----====  ВЫБОР ФАЙЛА  ====----
@dp.callback_query_handler(CallFilterForButtonValueFile(), state='*')
async def button_ask_file(call: types.CallbackQuery, state: FSMContext):
    def file_keyb():
        keyb = InlineKeyboardMarkup(row_width=1)
        for file in f_db.files:
            keyb.add(InlineKeyboardButton(text=f'Выбрать {file}', callback_data=f'b_set_f/{num_butt}/{tool}/{file}'))
        keyb.add(InlineKeyboardButton(text=f'Выбрать None', callback_data=f'b_set_f/{num_butt}/{tool}/None'))
        return keyb
    type_menu = 'id_msg_values'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    num_butt = query[1]
    button = buttons_db.button_numbers[num_butt]
    tool = query[2]
    tool_name = Data.button_tools[tool]
    keyboard = file_keyb()
    text = f"Выберите {tool_name} кнопки '{button}':"

    await state.finish()
    await create_menu_cancel(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await state.set_state(FCM.waite_set_file.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


@dp.callback_query_handler(CallFilter(startswith='b_set_f'), state=FCM.waite_set_file)
async def button_ask_file_2(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_values'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    num_butt = query[1]
    button = buttons_db.button_numbers[num_butt]
    tool = query[2]
    file = query[3]
    tool_text = Data.button_tools[tool]
    text = f"Файл '{file}' '{tool_text}' для кнопки '{button}' выбран."

    await state.finish()
    await create_menu_back(chat_id=chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        await change_button_tool(button, tool, file)
    except exceptions.PostgresError:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=f"Файл установить не удалось!")
        await log.write(
            f"admin_menu: {tool_text} '{file}' для кнопки '{button}' НЕ выбран. ({call.from_user.username})")
    else:
        await edit_message(chat_id=chat_id,
                           type_menu='id_msg_tools',
                           keyboard=(await button_tools_keyboard(button, num_butt, chat_id)),
                           text=f"{tool_text} '{file}' для кнопки '{button}' выбран.")
        await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
        await log.write(f"admin_menu: {tool_text} '{file}' для кнопки '{button}' выбран. ({call.from_user.username})")


#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====----
@dp.callback_query_handler(CallFilter(startswith='bt_value'), state='*')
async def button_ask_value(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_values'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    num_butt = query[1]
    button = buttons_db.button_numbers[num_butt]
    tool = query[2]
    tool_text = Data.button_tools[tool]
    text = f"Введите значение параметра '{tool_text}' для кнопки '{button}'"

    await state.finish()
    await create_menu_cancel(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await adm_chats_db.write(chat_id=chat_id, tools=['option', 'tool'], values=[num_butt, tool])
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
    await state.set_state(FCM.waite_butt_value.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_butt_value)
async def button_read_value(message: types.Message, state: FSMContext):
    type_menu = 'id_msg_values'
    chat_id = message.chat.id
    num_butt = adm_chats_db.chats[chat_id].option
    button = buttons_db.button_numbers[num_butt]
    tool = adm_chats_db.chats[chat_id].tool
    value = message.text
    tool_text = Data.button_tools[tool]
    text = f"Значение '{value}' параметра '{tool_text}' для кнопки '{button}' установлено."

    await state.finish()
    await create_menu_back(chat_id=chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        await change_button_tool(button, tool, value)
    except exceptions.PostgresError:
        answer = f"Значение '{value}' параметра '{tool_text}' для кнопки '{button}' не установлено!"
        await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
        await log.write(f"admin_menu: Значение '{value}' параметра '{tool_text} ({tool})' для кнопки '{button}' "
                        f"НЕ установлено!, ({message.from_user.username})")
    else:
        if tool == "name":
            button_name = value
            await edit_message(chat_id=chat_id,
                               type_menu='id_msg_options',
                               keyboard=(await buttons_keyboard(chat_id)),
                               text=f"Кнопка {button} переименована")
        else:
            button_name = button
        await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
        #  Обновление сообщения с tools
        await edit_message(chat_id=chat_id,
                           type_menu='id_msg_tools',
                           keyboard=(await button_tools_keyboard(button_name, num_butt, chat_id)),
                           text=text)
        await log.write(f"admin_menu: Значение '{value}' параметра '{tool_text} ({tool})' для кнопки '{button}'"
                        f" установлено, ({message.from_user.username})")
