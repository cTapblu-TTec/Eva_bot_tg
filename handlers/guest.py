from contextlib import suppress
from aiogram import types

from aiogram.utils.exceptions import BadRequest

from filters.users_filters import FilterForGuest, CallFilterForGuest
from loader import dp
from utils.log import log


# все сообщения от гостей
@dp.message_handler(FilterForGuest(), state="*")
async def guest(message: types.Message):
    with suppress(BadRequest):
        await message.answer("Извините, у Вас нет доступа к боту")
    await log.write(f'Гость: "{message.text}", ({message.from_user.username} - {message.from_user.id})')


@dp.callback_query_handler(CallFilterForGuest(), state="*")
async def errors_call(call: types.CallbackQuery):
    with suppress(BadRequest):
        await call.message.answer("Извините, у Вас нет доступа к боту")
        await call.answer()
    await log.write(f'Гость: call.data: "{call.data}", ({call.from_user.username} - {call.from_user.id})')
