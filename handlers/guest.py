from contextlib import suppress
from aiogram import types

from aiogram.utils.exceptions import BadRequest

from filters.users_filters import FilterForGuest
from loader import dp
from utils.log import log


# все сообщения от гостей
@dp.message_handler(FilterForGuest(), state="*")
async def guest(message: types.Message):
    user_name = message.from_user.username
    if user_name not in ('None', None):
        user_name = '@' + user_name
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    user_id = message.from_user.id
    with suppress(BadRequest):
        await message.answer("Извините, у Вас нет доступа к боту")
    await log.write(f'Гость: "{message.text}", ({first_name} {last_name}, Ник: {user_name}, id: {user_id})', 'admin')


@dp.callback_query_handler(FilterForGuest(), state="*")
async def errors_call(call: types.CallbackQuery):
    with suppress(BadRequest):
        await call.message.answer("Извините, у Вас нет доступа к боту")
        await call.answer()
    await log.write(f'Гость: call.data: "{call.data}", ({call.from_user.username} - {call.from_user.id})', 'admin')
