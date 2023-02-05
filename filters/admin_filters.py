from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter


# --== КНОПКИ ==--
class CallFilterForButtonTools(BoundFilter):
    async def check(self,  callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'b_tool':
                return True
        return False


class CallFilterForButtonDell(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if callback.data[:11] == 'dell_button':
            return True
        return False


class CallFilterForButtonValueFile(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if (query[0] == 'bt_value') and ('file' in query[2]):
                return True
        return False


class CallFilterForButtonValue(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'bt_value':
                return True
        return False


class CallFilterForButtonValueSetFile(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'b_set_f':
                return True
        return False


# --== ГРУППЫ ==--
class CallFilterForGroupTools(BoundFilter):
    async def check(self,  callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'g_tool':
                return True
        return False


# todo попробовать сделать для разных хендлеров - if data['filter'] == 'параметр из хендлера'
class CallFilterForGroupValue(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'gr_value':
                return True
        return False


class CallFilterForGroupDell(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'dell_group':
                return True
        return False


# --== ФАЙЛЫ ==--
class CallFilterForFileValue(BoundFilter):
    async def check(self,  callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'f_value':
                return True
        return False


def registry_admin_filters(dp: Dispatcher):
    dp.filters_factory.bind(CallFilterForGroupValue)
    dp.filters_factory.bind(CallFilterForButtonTools)
    dp.filters_factory.bind(CallFilterForButtonDell)
    dp.filters_factory.bind(CallFilterForGroupTools)
    dp.filters_factory.bind(CallFilterForGroupDell)
    dp.filters_factory.bind(CallFilterForButtonValue)
    dp.filters_factory.bind(CallFilterForFileValue)
