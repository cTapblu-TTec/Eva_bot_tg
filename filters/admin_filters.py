from aiogram import Dispatcher
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery

from data.config import ADMINS


# --== УНИВЕРСАЛЬНЫЙ ФИЛЬТР ==--
class CallFilter(BoundFilter):
    def __init__(self, startswith: str) -> None:
        self.startswith = startswith

    async def check(self, callback: CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == self.startswith:
                return True
        return False


class FilterCheckAdmin(BoundFilter):
    async def check(self, query):
        user_id = query.from_user.id
        if user_id in ADMINS:
            return True
        return False


# --== КНОПКИ ==--
class CallFilterForButtonValueFile(BoundFilter):
    async def check(self, callback: CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if (query[0] == 'bt_value') and ('file' in query[2]):
                return True
        return False


def registry_admin_filters(dp: Dispatcher):

    dp.filters_factory.bind(CallFilter)
    dp.filters_factory.bind(CallFilterForButtonValueFile)
    dp.filters_factory.bind(FilterCheckAdmin)

