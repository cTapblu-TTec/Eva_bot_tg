from filters.users_filters import FilterForGuest, CallFilterForGuest
from loader import dp


# все сообщения от гостей
@dp.message_handler(FilterForGuest(), state="*")
async def guest(message):
    pass


@dp.callback_query_handler(CallFilterForGuest(), state="*")
async def errors_call(call):
    pass
