from dataclasses import dataclass

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

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
    replykeyboard_back: bool = False
    replykeyboard_cancel: bool = False


class FCM(StatesGroup):
    waite_value = State()


#  ----====  ВЫБОР КНОПКИ ====----
@dp.message_handler(commands="settings", state='*')
async def settings_button(message: types.Message, state: FSMContext):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return
    await state.finish()
    await message.answer("Создано меню 'Назад'",
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад'))
    Data.replykeyboard_back = True
    Data.replykeyboard_cancel = False
    Data.tools_msg_id = None
    Data.buttons_msg_id = None

    # START HANDLER
    keyboard = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
    for button in buttons_db.buttons_names:
        inline_button = InlineKeyboardButton(text=button, callback_data=button)
        keyboard.add(inline_button)
    # FINISH HANDLER
    msg = await message.answer("Выберите кнопку для настройки:", reply_markup=keyboard)
    Data.buttons_msg_id = msg["message_id"]

    # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")


#  ----====  ВЫБОР ПАРАМЕТРА КНОПКИ  ====----
@dp.callback_query_handler(ChekButtonsForCallback(), state="*")
async def settings_button_tool(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if not Data.replykeyboard_back:
        await call.message.answer("Создано меню 'Назад'",
                                  reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад'))
        Data.replykeyboard_back = True
    # START HANDLER
    button = call.data

    tools_b = [a for a in dir(buttons_db.buttons[button]) if not a.startswith('__')]
    keyboard = InlineKeyboardMarkup(row_width=1)
    for tool in tools_b:
        value = getattr(buttons_db.buttons[button], tool)
        inline_button = InlineKeyboardButton(text=f'{tool} --==-- {value}', callback_data=f'{button}/{tool}')
        keyboard.add(inline_button)
    # FINISH HANDLER
    if Data.tools_msg_id:
        await dp.bot.edit_message_text(chat_id=call.message.chat.id,
                                       message_id=Data.tools_msg_id,
                                       reply_markup=keyboard,
                                       text=f"Выберите параметр кнопки '{button}' для настройки:")
    else:
        msg = await call.message.answer(f"Выберите параметр кнопки '{button}' для настройки:", reply_markup=keyboard)
        Data.tools_msg_id = msg["message_id"]
    await call.answer()


#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====----
@dp.callback_query_handler(state='*')
async def settings_button_tool(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if not Data.replykeyboard_cancel:
        await call.message.answer("Создано меню 'Отмена'",
                                  reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена'))
        Data.replykeyboard_cancel = True
        Data.replykeyboard_back = False

    # START HANDLER
    query = call.data.split('/')
    button = query[0]
    tool = query[1]
    tools_b = [a for a in dir(buttons_db.buttons[button]) if not a.startswith('__')]

    if tool not in tools_b:
        await call.message.answer(
            f"Выберите параметр кнопки '{button}' для настройки")
        return

    Data.query = {'button': button, 'tool': tool}

    # FINISH HANDLER
    await call.message.answer(f"Введите значение параметра '{tool}' для кнопки '{button}'")
    await state.set_state(FCM.waite_value.state)
    await call.answer()


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_value)
async def settings_button_tool(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Отмена':
        await message.answer("Отменено", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад'))
        Data.replykeyboard_cancel = False
        Data.replykeyboard_back = True
        return

    # START HANDLER
    button = Data.query['button']
    tool = Data.query['tool']
    value = message.text
    try:
        await buttons_db.write(button, [tool], [value])

        # Обновление сообщения с tools
        if Data.tools_msg_id:
            tools_b = [a for a in dir(buttons_db.buttons[button]) if not a.startswith('__')]
            keyboard = InlineKeyboardMarkup(row_width=1)
            for tool_m in tools_b:
                value_m = getattr(buttons_db.buttons[button], tool_m)
                inline_button = InlineKeyboardButton(text=f'{tool_m} --==-- {value_m}', callback_data=f'{button}/{tool_m}')
                keyboard.add(inline_button)
            await dp.bot.edit_message_text(chat_id=message.chat.id,
                                           message_id=Data.tools_msg_id,
                                           reply_markup=keyboard,
                                           text=f"Значение '{value}' параметра '{tool}'"
                                                f" для кнопки '{button}' установлено.")

        await message.answer(f"Значение '{value}' параметра '{tool}' для кнопки '{button}' установлено.",
                             reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад'))
        Data.replykeyboard_cancel = False
        Data.replykeyboard_back = True
        if tool in ["name","group_buttons","active"]:
            await buttons_db.create()
            await groups_db.create(None)

            await message.answer("Данные обновлены из базы данных")

        await log(f"admin: Значение '{value}' параметра '{tool}' для кнопки '{button}' установлено,"
                  f" ({message.from_user.username})\n")

    except:
        await message.answer(f"Значение '{value}' параметра '{tool}' для кнопки '{button}' не установлено!\n"
                             f"Введите новое значение")
        await state.set_state(FCM.waite_value.state)

# await log(f'admin: {message.text}, ({message.from_user.username})\n')
