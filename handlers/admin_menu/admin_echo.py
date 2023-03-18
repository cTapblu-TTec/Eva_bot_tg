from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from utils.admin_menu_utils import create_menu_back, delete_last_menu
from loader import dp
from handlers.separation import keyboard_groups


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def echo(message: types.Message):

    username = message.from_user.username
    is_admin = message.chat.id in ADMINS
    keyboard = await keyboard_groups(username, is_admin)
    await message.answer("Группы кнопок для волонтерства:", reply_markup=keyboard)


# Эхо хендлер, куда летят не обработанные калбеки (ошибки)
@dp.callback_query_handler(state='*')
async def errors_call(call: types.CallbackQuery, state: FSMContext):
    # st = await state.get_state()
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await delete_last_menu(call.message.chat.id)
    await call.message.answer("Отменено")

    # await call.message.answer("Что-то пошло не так")
    # print(f'Ошибка кнопок, call.data: {call.data}, state:', st)
    # await log.write(f"Ошибка кнопок, call.data: '{call.data}', state:', {st} ({call.from_user.username})")
    await call.answer()


# Эхо хендлер, куда летят не обработанные сообщения (ошибки)
@dp.message_handler(state='*')
async def errors_mess(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    await delete_last_menu(message.chat.id)
    await message.answer("Отменено")

    # await message.answer("Что-то пошло не так")
    # print(f'admin: Ошибка сообщений, message: {message.text}, state:', state)
    # await log.write(f"admin: Ошибка кнопок, message: '{message.text}' ({message.from_user.username})")
