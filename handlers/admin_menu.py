from contextlib import suppress
from dataclasses import dataclass

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from filters.chek_buttons import ChekButtonsForCallback
from loader import dp
from utils.face_control import control
from utils.log import log
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db


@dataclass()
class Data:
    query = {}
    buttons_msg_id: int = None
    tools_msg_id: int = None
    menu_back: bool = False
    menu_cancel: bool = False
    tools_b = []
    names_tools = {'name': 'Имя кнопки', 'group_buttons': 'Меню кнопок', 'work_file': 'Файл отметок',
                   'num_block': '№ блока', 'size_blok': 'кол-во отметок', 'name_block': 'Текст после №',
                   'shablon_file': 'Файл шаблона', 'active': 'Вкл/Выкл (1/0)', 'sort': 'Порядок в меню',
                   'hidden': 'Скрытая кнопка (1/0)', 'users': 'Кому доступ скрытой', 'specification': 'Описание'}


class FCM(StatesGroup):
    waite_value = State()


async def tools_keyboard(button, tools_b):
    print(buttons_db.buttons[button])
    keyboard = InlineKeyboardMarkup(row_width=1)
    for tool in tools_b:
        value = getattr(buttons_db.buttons[button], tool)
        if tool in Data.names_tools:
            tool_text = Data.names_tools[tool]
        else:
            tool_text = tool
        inline_button = InlineKeyboardButton(text=f'{tool_text} --==-- {value}', callback_data=f'{button}/{tool}')
        keyboard.add(inline_button)
    return keyboard


#  ----====  ВЫБОР КНОПКИ ====----
@dp.message_handler(commands="settings", state='*')
async def settings_button(message: types.Message, state: FSMContext):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return
    await state.finish()
    await message.answer("Создано меню 'Назад'",
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад', '/settings'))
    if Data.tools_msg_id:
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await dp.bot.delete_message(chat_id=message.chat.id, message_id=Data.tools_msg_id)
    if Data.buttons_msg_id:
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await dp.bot.delete_message(chat_id=message.chat.id, message_id=Data.buttons_msg_id)

    Data.menu_back = True
    Data.menu_cancel = False
    Data.tools_msg_id = None

    # START HANDLER
    keyboard = InlineKeyboardMarkup(row_width=1)
    for button in buttons_db.buttons_names:
        inline_button = InlineKeyboardButton(text=button, callback_data=button)
        keyboard.add(inline_button)
    # FINISH HANDLER
    msg = await message.answer("Выберите кнопку для настройки:", reply_markup=keyboard)
    Data.buttons_msg_id = msg["message_id"]


#  ----====  ВЫБОР ПАРАМЕТРА КНОПКИ  ====----
@dp.callback_query_handler(ChekButtonsForCallback(), state="*")
async def settings_button_tool(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if not Data.menu_back:
        await call.message.answer("Создано меню 'Назад'",
                                  reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад',
                                                                                                   '/settings'))
        Data.menu_back = True
        Data.menu_cancel = False
    # START HANDLER
    button = call.data
    Data.tools_b = [a for a in dir(buttons_db.buttons[button]) if not a.startswith('__')]

    keyboard = await tools_keyboard(button, Data.tools_b)
    # FINISH HANDLER
    if Data.tools_msg_id:
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await dp.bot.edit_message_text(chat_id=call.message.chat.id,
                                           message_id=Data.tools_msg_id,
                                           reply_markup=keyboard,
                                           text=f"Выберите параметр кнопки '{button}' для настройки:")
    else:
        msg = await call.message.answer(f"Выберите параметр кнопки '{button}' для настройки:", reply_markup=keyboard)
        Data.tools_msg_id = msg["message_id"]
    await call.answer()


#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====---- todo: возможно смело так обрабатывать все калбеки
@dp.callback_query_handler(state='*')
async def settings_button_tool(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if not Data.menu_cancel:
        await call.message.answer("Создано меню 'Отмена'",
                                  reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена'))
        Data.menu_cancel = True
        Data.menu_back = False

    # START HANDLER
    if '/' in call.data[1:]:
        query = call.data.split('/')
        button = query[0]
        tool = query[1]
    else:
        await call.message.answer(f"Что-то пошло не так, нажмите /settings")
        return

    if tool not in Data.tools_b:
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


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_value)
async def settings_button_tool(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Отмена':
        await message.answer("Отменено",
                             reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад', '/settings'))
        Data.menu_cancel = False
        Data.menu_back = True
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

        await message.answer(f"Значение '{value}' параметра '{tool_text}' для кнопки '{button}' установлено.",
                             reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад', '/settings'))
        Data.menu_cancel = False
        Data.menu_back = True

        #  Обновление сообщения с tools
        if tool == "name":
            button_name = value
        else:
            button_name = button
        if Data.tools_msg_id:
            with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
                keyboard = await tools_keyboard(button_name, Data.tools_b)
                await dp.bot.edit_message_text(chat_id=message.chat.id,
                                               message_id=Data.tools_msg_id,
                                               reply_markup=keyboard,
                                               text=f"Значение '{value}' параметра '{tool_text}'"
                                                    f" для кнопки '{button}' установлено.")

        await log(f"admin: Значение '{value}' параметра '{tool_text} ({tool})' для кнопки '{button}' установлено,"
                  f" ({message.from_user.username})\n")

    except:
        await message.answer(f"Значение '{value}' параметра '{tool_text}' для кнопки '{button}' не установлено!\n"
                             f"Введите новое значение")
        await state.set_state(FCM.waite_value.state)

        await log(f"admin: Значение '{value}' параметра '{tool_text} ({tool})' для кнопки '{button}' НЕ установлено!,"
                  f" ({message.from_user.username})\n")

