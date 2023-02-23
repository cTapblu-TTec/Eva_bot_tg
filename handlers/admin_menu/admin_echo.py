from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.admin_menu_utils import create_menu_back, delete_last_menu
from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def echo(message: types.Message):
    echo_buttons = ['Волонтерство', 'Дополнительные функции']
    keyboard = InlineKeyboardMarkup(row_width=1)
    for butt in echo_buttons:
        inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
        keyboard.add(inline_button)
    await message.answer("Eva_bot:", reply_markup=keyboard)


# Эхо хендлер, куда летят не обработанные калбеки (ошибки)
@dp.callback_query_handler(state='*')
async def errors_call(call: types.CallbackQuery, state: FSMContext):
    # st = await state.get_state()
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await delete_last_menu(call.message.chat.id)
    # await call.message.answer("Что-то пошло не так, нажмите /settings")
    # print(f'Ошибка кнопок, call.data: {call.data}, state:', st)
    # await log.write(f"Ошибка кнопок, call.data: '{call.data}', state:', {st} ({call.from_user.username})")
    await call.answer()


# Эхо хендлер, куда летят не обработанные сообщения (ошибки)
@dp.message_handler(state='*')
async def errors_mess(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    await delete_last_menu(message.chat.id)
    # await message.answer("Что-то пошло не так, нажмите /settings")
    # print(f'admin: Ошибка сообщений, message: {message.text}, state:', state)
    # await log.write(f"admin: Ошибка кнопок, message: '{message.text}' ({message.from_user.username})")
