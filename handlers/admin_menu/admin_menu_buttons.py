from dataclasses import dataclass

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from filters.admin_filters import CallFilterForButtonTools, CallFilterForButtonDell, CallFilterForButtonValue, \
    CallFilterForButtonValueFile, CallFilterForButtonValueSetFile
from loader import dp
from utils.admin_utils import get_button_clicks
from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_groups_buttons import groups_db
from utils.admin_menu_utils import dellete_old_message, create_menu_back, create_menu_cancel, edit_message, \
    delete_all_after_time


@dataclass()
class Data:
    query = {}
    tools_b = []
    names_tools = {'name': 'Имя кнопки', 'group_buttons': 'Меню кнопок', 'work_file': 'Файл отметок',
                   'num_block': '№ блока', 'size_blok': 'кол-во отметок', 'name_block': 'Текст после №',
                   'shablon_file': 'Файл шаблона', 'active': 'Вкл/Выкл (1/0)', 'sort': 'Порядок в меню',
                   'hidden': 'Скрытая кнопка (1/0)', 'users': 'Кому доступ скрытой', 'specification': 'Описание'}


class FCM(StatesGroup):
    waite_value = State()
    waite_set_file = State()


async def tools_keyboard(button):
    keyboard = InlineKeyboardMarkup(row_width=1)
    Data.tools_b = [a for a in dir(buttons_db.buttons[button]) if not a.startswith('__')]
    for tool in Data.tools_b:
        value = getattr(buttons_db.buttons[button], tool, None)
        if tool in Data.names_tools:
            tool_text = Data.names_tools[tool]
        else:
            tool_text = tool
        inline_button = InlineKeyboardButton(text=f'{tool_text} --==-- {value}',
                                             callback_data=f'bt_value/{button}/{tool}')
        keyboard.add(inline_button)
    keyboard.add(InlineKeyboardButton(text='Удалить кнопку', callback_data='dell_button|' + button))

    return keyboard


async def buttons_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for button in buttons_db.buttons_names:
        cliks = await get_button_clicks(button)
        button_cliks = ''
        if cliks: button_cliks = f' - {cliks}'
        keyboard.add(InlineKeyboardButton(text=f'{button}{button_cliks}', callback_data='b_tool/' + button))
    keyboard.add(InlineKeyboardButton(text='Добавить кнопку', callback_data='add_button'))
    return keyboard


# ____________________________________ask_options____________________________________
#  ----====  ВЫБОР КНОПКИ ====----
@dp.callback_query_handler(text="Настройка кнопок", state='*')
async def buttons_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_options')
    keyboard = await buttons_keyboard()
    msg = await call.message.answer("Кнопка - осталось нажатий:", reply_markup=keyboard)
    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_options'], values=[msg["message_id"]])
    await call.answer()

    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    await delete_all_after_time(call.message.chat.id)


# ____________________________________ask_tools____________________________________
#  ----====  ДОБАВИТЬ КНОПКУ ====----
@dp.callback_query_handler(text='add_button', state='*')
async def add_button(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if 'Новая кнопка' not in buttons_db.buttons:
        await buttons_db.write('Новая кнопка', 'add_button', '')
        await edit_message(chat_id=call.message.chat.id,
                           type_menu='id_msg_options',
                           keyboard=(await buttons_keyboard()),
                           text="Кнопка 'Новая кнопка' добавлена")
        await call.message.answer("Кнопка 'Новая кнопка' добавлена, можете ее переименовать /settings")
    else:
        await call.message.answer("Кнопка 'Новая кнопка' уже есть, можете ее переименовать /settings")
    await call.answer()
    await log.write(f"admin: Кнопка добавлена ({call.from_user.username})\n")


#  ----====  УДАЛИТЬ КНОПКУ ====----
@dp.callback_query_handler(CallFilterForButtonDell(), state='*')
async def dell_button(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    button = call.data[12:]
    if button in buttons_db.buttons:
        await buttons_db.write(button, 'dell_button', '')
        await edit_message(chat_id=call.message.chat.id,
                           type_menu='id_msg_options',
                           keyboard=(await buttons_keyboard()),
                           text=f"Кнопка {button} удалена")
        await call.message.answer(f"Кнопка {button} удалена")
        await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    else:
        await call.message.answer(f"Кнопка {button} не найдена")
    await call.answer()
    await log.write(f"admin: Кнопка {button} удалена ({call.from_user.username})\n")
    await delete_all_after_time(call.message.chat.id)


#  ----====  ВЫБОР ПАРАМЕТРА КНОПКИ  ====----
@dp.callback_query_handler(CallFilterForButtonTools(), state="*")
async def button_tools(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    # id_msg_tools
    query = call.data.split('/')
    button = query[1]
    keyboard = await tools_keyboard(button)
    msg = await call.message.answer(f"Выберите параметр кнопки '{button}' для настройки:", reply_markup=keyboard)
    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_tools'], values=[msg["message_id"]])
    await call.answer()

    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    await delete_all_after_time(call.message.chat.id)


# ____________________________________ask_values____________________________________
#  ----====  ВЫБОР ФАЙЛА  ====----
@dp.callback_query_handler(CallFilterForButtonValueFile(), state='*')
async def button_ask_value(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    query = call.data.split('/')
    button = query[1]
    tool = query[2]
    tool_name = Data.names_tools[tool]
    keyboard = InlineKeyboardMarkup(row_width=1)
    for file in f_db.files:
        keyboard.add(InlineKeyboardButton(text=f'Выбрать {file}', callback_data=f'b_set_f/{button}/{tool}/{file}'))
    keyboard.add(InlineKeyboardButton(text=f'Выбрать None', callback_data=f'b_set_f/{button}/{tool}/None'))
    msg = await call.message.answer(f"Выберите {tool_name} кнопки '{button}':", reply_markup=keyboard)
    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_values'], values=[msg["message_id"]])
    await state.set_state(FCM.waite_set_file.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


@dp.callback_query_handler(CallFilterForButtonValueSetFile(), state=FCM.waite_set_file)
async def button_ask_value(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    query = call.data.split('/')
    button = query[1]
    tool = query[2]
    file = query[3]
    tool_text = Data.names_tools[tool]
    try:
        await buttons_db.write(button, [tool], [file])
        await create_menu_back(chat_id=call.message.chat.id,
                               text=f"Файл '{file}' '{tool_text}' для кнопки '{button}' выбран.")

        await edit_message(chat_id=call.message.chat.id,
                           type_menu='id_msg_tools',
                           keyboard=(await tools_keyboard(button)),
                           text=f"{tool_text} '{file}' для кнопки '{button}' выбран.")

        await log.write(f"admin: {tool_text} '{file}' для кнопки '{button}' выбран."
                        f" ({call.from_user.username})\n")
    except Exception:
        await call.message.answer(f"Файл установить не удалось!\n")
        await log.write(f"admin: {tool_text} '{file}' для кнопки '{button}' НЕ выбран. ({call.from_user.username})")


#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====----
@dp.callback_query_handler(CallFilterForButtonValue(), state='*')
async def button_ask_value(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    # id_msg_value
    # START HANDLER
    query = call.data.split('/')
    button = query[1]
    tool = query[2]

    if tool not in Data.tools_b:
        print(f'data={call.data}')
        await call.message.answer(f"Выберите параметр кнопки '{button}' для настройки")
        return

    Data.query = {'button': button, 'tool': tool}

    # FINISH HANDLER
    if tool in Data.names_tools:
        tool_text = Data.names_tools[tool]
    else:
        tool_text = tool
    await call.message.answer(f"Введите значение параметра '{tool_text}' для кнопки '{button}'")
    await state.set_state(FCM.waite_value.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_value)
async def button_read_value(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Отмена':
        await create_menu_back(message.chat.id)
        return

    # START HANDLER
    button = Data.query['button']
    tool = Data.query['tool']
    value = message.text
    if tool in Data.names_tools:
        tool_text = Data.names_tools[tool]
    else:
        tool_text = tool

    try:
        await buttons_db.write(button, [tool], [value])
        if tool in ["name", "group_buttons", "active", "sort"]:
            await buttons_db.create()
            await groups_db.create(None)
            await message.answer("Данные обновлены из базы данных")

        await create_menu_back(chat_id=message.chat.id,
                               text=f"Значение '{value}' параметра '{tool_text}' для кнопки '{button}' установлено.")

        if tool == "name":
            button_name = value
            await edit_message(chat_id=message.chat.id,
                               type_menu='id_msg_options',
                               keyboard=(await buttons_keyboard()),
                               text=f"Кнопка {button} переименована")

        else:
            button_name = button
        #  Обновление сообщения с tools
        await edit_message(chat_id=message.chat.id,
                           type_menu='id_msg_tools',
                           keyboard=(await tools_keyboard(button_name)),
                           text=f"Значение '{value}' параметра '{tool_text}' для кнопки '{button}' установлено.")

        await log.write(f"admin: Значение '{value}' параметра '{tool_text} ({tool})' для кнопки '{button}' установлено,"
                        f" ({message.from_user.username})\n")

    except Exception:
        await message.answer(f"Значение '{value}' параметра '{tool_text}' для кнопки '{button}' не установлено!\n"
                             f"Введите новое значение")
        await state.set_state(FCM.waite_value.state)

        await log.write(f"admin: Значение '{value}' параметра '{tool_text} ({tool})' для кнопки '{button}' "
                        f"НЕ установлено!, ({message.from_user.username})\n")
