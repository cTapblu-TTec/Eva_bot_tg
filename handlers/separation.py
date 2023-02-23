from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from filters.users_filters import FilterForStart, CallFilterForError
from loader import dp
from utils.admin_menu_utils import create_menu_back, delete_last_menu
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
    await call.message.answer(f"Отменено")
    if call.data != "Отмена":
        await log.write(f"Ошибка кнопок, call.data: '{call.data}' ({call.from_user.username})")
    await call.answer()


# первый хендлер для админов
@dp.message_handler(text='Отмена', state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    await delete_last_menu(message.chat.id)