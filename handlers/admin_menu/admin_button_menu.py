from dataclasses import dataclass

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from filters.callback_filters import ChekButtonsForCallback, ChekDellButton
from loader import dp
from utils.admin_utils import get_button_clicks
from utils.face_control import control
from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_buttons import buttons_db
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


async def tools_keyboard(button):
    keyboard = InlineKeyboardMarkup(row_width=1)
    Data.tools_b = [a for a in dir(buttons_db.buttons[button]) if not a.startswith('__')]
    for tool in Data.tools_b:
        value = getattr(buttons_db.buttons[button], tool, None)
        if tool in Data.names_tools:
            tool_text = Data.names_tools[tool]
        else:
            tool_text = tool
        inline_button = InlineKeyboardButton(text=f'{tool_text} --==-- {value}', callback_data=f'{button}/{tool}')
        keyboard.add(inline_button)
    keyboard.add(InlineKeyboardButton(text='Удалить кнопку', callback_data='dell_button|' + button))
    return keyboard


async def buttons_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for button in buttons_db.buttons_names:
        cliks = await get_button_clicks(button)
        button_cliks = ''
        if cliks: button_cliks = f' - {cliks}'
        keyboard.add(InlineKeyboardButton(text=f'{button}{button_cliks}', callback_data=button))
    keyboard.add(InlineKeyboardButton(text='Добавить кнопку', callback_data='add_button'))
    return keyboard


#  ----====  ВЫБОР КНОПКИ ====----
@dp.callback_query_handler(text="Настройка кнопок", state='*')
async def settings_button(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_options')
    # id_msg_options
    keyboard = await buttons_keyboard()
    msg = await call.message.answer("Кнопка - осталось нажатий:", reply_markup=keyboard)
    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_options'], values=[msg["message_id"]])
    await call.answer()

    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    await delete_all_after_time(call.message.chat.id)


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
        await call.message.answer("Кнопка 'Новая кнопка' добавлена, можете ее настроить /settings")
    else:
        await call.message.answer("Кнопка 'Новая кнопка' уже есть, можете ее настроить /settings")
    await call.answer()
    await log.write(f"admin: Кнопка добавлена ({call.message.chat.username})\n")


#  ----====  УДАЛИТЬ КНОПКУ ====----
@dp.callback_query_handler(ChekDellButton(), state='*')
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
    await log.write(f"admin: Кнопка {button} удалена ({call.message.chat.username})\n")
    await delete_all_after_time(call.message.chat.id)


#  ----====  ВЫБОР ПАРАМЕТРА КНОПКИ  ====----
@dp.callback_query_handler(ChekButtonsForCallback(), state="*")
async def settings_button_tool(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    # id_msg_tools
    button = call.data
    keyboard = await tools_keyboard(button)
    msg = await call.message.answer(f"Выберите параметр кнопки '{button}' для настройки:", reply_markup=keyboard)
    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_tools'], values=[msg["message_id"]])
    await call.answer()

    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    await delete_all_after_time(call.message.chat.id)


#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====---- todo: возможно смело так обрабатывать все калбеки
@dp.callback_query_handler(state='*')
async def settings_button_tool(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    # id_msg_value
    # START HANDLER
    if '/' in call.data[1:]:
        query = call.data.split('/')
        button = query[0]
        tool = query[1]
    else:
        await call.message.answer(f"Что-то пошло не так, нажмите /settings")
        print(f'data={call.data}', await state.get_state())

        await log.write(f"admin: Что-то пошло не так, call.data: '{call.data}' ({call.from_user.username})\n")
        return

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
async def settings_button_tool(message: types.Message, state: FSMContext):
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
        if tool in ["name", "group_buttons", "active"]:
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

        await log.write(f"admin: Значение '{value}' параметра '{tool_text} ({tool})' для кнопки '{button}' НЕ установлено!,"
                  f" ({message.from_user.username})\n")


@dp.message_handler(state='*', text='Отмена')
async def cancel(message: types.Message, state: FSMContext):
    user = await control(message)  # проверяем статус пользователя
    if user == 'admin':
        await adm_chats_db.write(chat_id=message.chat.id, tools=['menu_back', 'menu_cancel'], values=['false', 'true'])
        await create_menu_back(chat_id=message.chat.id)
        await state.finish()
