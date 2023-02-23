from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter


from data.config import ADMINS
from utils.face_control import control
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db


class FilterForStart(BoundFilter):
    async def check(self, message: types.Message):
        user = await control(message.from_user.id, message.from_user.username)
        if user == "user":
            return True
        return False


class FilterForGuest(BoundFilter):
    async def check(self, message: types.Message):
        user = await control(message.from_user.id, message.from_user.username)
        if user == "guest":
            return True
        return False


class FilterForGeneral(BoundFilter):
    async def check(self, message: types.Message):
        if message.text in buttons_db.buttons_names and buttons_db.buttons[message.text].active == 1:
            return True
        return False


class FilterForBattonsMenu(BoundFilter):
    async def check(self, message: types.Message):
        group = message.text
        if group in buttons_db.buttons_groups:
            if groups_db.groups[group].hidden == 0:
                return True
            else:
                if message.from_user.id in ADMINS:
                    return True
                if groups_db.groups[group].users and \
                        message.from_user.username in groups_db.groups[group].users:
                    return True
        return False


class CallFilterForBattonsMenu(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'menu_groups':
                group = query[1]
                if group in buttons_db.buttons_groups:
                    if groups_db.groups[group].hidden == 0:
                        return True
                    else:
                        if callback.message.chat.id in ADMINS:
                            return True
                        if groups_db.groups[group].users and \
                                callback.message.chat.username in groups_db.groups[group].users:
                            return True
                return True
        return False


class CallFilterForError(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        # проверяем статус пользователя
        if callback.message.chat.id not in ADMINS:
            return True
        return False


class CallFilterForGuest(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        # проверяем статус пользователя
        user = await control(callback.from_user.id, callback.from_user.username)
        if user == "guest":
            return True
        return False


class CallFilterForBlocksUser(BoundFilter):
    async def check(self,  callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'u_blocks':
                return True
        return False


def registry_user_filters(dp: Dispatcher):
    dp.filters_factory.bind(FilterForGeneral)
    dp.filters_factory.bind(FilterForBattonsMenu)
    dp.filters_factory.bind(CallFilterForBattonsMenu)
    dp.filters_factory.bind(FilterForGuest)
    dp.filters_factory.bind(FilterForStart)
    dp.filters_factory.bind(CallFilterForError)
    dp.filters_factory.bind(CallFilterForGuest)
    dp.filters_factory.bind(CallFilterForBlocksUser)
