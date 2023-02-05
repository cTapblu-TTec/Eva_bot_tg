from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from filters.users_filters import FilterForStart, CallFilterForError
from loader import dp
from utils.log import log


# все сообщения от пользователей
@dp.message_handler(FilterForStart(), state="*")
async def start(message: types.Message):

    echo_buttons = ['Волонтерство', 'Дополнительные функции']
    keyboard = InlineKeyboardMarkup(row_width=1)
    for butt in echo_buttons:
        inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
        keyboard.add(inline_button)
    await message.answer("Eva_bot:", reply_markup=keyboard)


# Эхо хендлер, куда летят не обработанные калбеки (ошибки) пользователей
@dp.callback_query_handler(CallFilterForError(), state='*')
async def errors_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    state = await state.get_state()
    await call.message.answer(f"Что-то пошло не так, нажмите /start")
    print(f'Ошибка кнопок, call.data: {call.data}, state:', state)
    await log.write(f"Ошибка кнопок, call.data: '{call.data}' ({call.from_user.username})\n")
    await call.answer()
