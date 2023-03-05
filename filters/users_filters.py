from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS
from utils.face_control import control
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_users import users_db


# ГОСТИ
class FilterForGuest(BoundFilter):
    async def check(self, message: types.Message):
        user = await control(message.from_user.id, message.from_user.username)
        if user == "guest":
            return True
        return False


class CallFilterForGuest(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        # проверяем статус пользователя
        user = await control(callback.from_user.id, callback.from_user.username)
        if user == "guest":
            return True
        return False


# ПОЛЬЗОВАТЕЛИ
class FilterForStart(BoundFilter):
    async def check(self, message: types.Message):
        user = await control(message.from_user.id, message.from_user.username)
        if user == "user":
            return True
        return False


class FilterForAskHowManyBlocks(BoundFilter):
    async def check(self, message: types.Message):
        button = message.text
        if button in buttons_db.buttons and buttons_db.buttons[message.text].active == 1\
                and users_db.users[message.from_user.username].use_many_blocks == 1:
            return True
        return False


class FilterForGeneral(BoundFilter):
    async def check(self, message: types.Message):
        num_x = message.text.rfind('Х')
        blocks_str = message.text[num_x + 1:]
        if blocks_str.isdigit() and 1 <= int(blocks_str) <= 10:
            button = message.text[:num_x - 1]
        else:
            button = message.text
        if button in buttons_db.buttons and buttons_db.buttons[button].active == 1:
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
        return False


class CallFilterForError(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        # проверяем статус пользователя
        if callback.message.chat.id not in ADMINS:
            return True
        return False


class CallFilterUser(BoundFilter):
    def __init__(self, startswith: str) -> None:
        self.startswith = startswith

    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == self.startswith:
                return True
        return False


def registry_user_filters(dp: Dispatcher):
    dp.filters_factory.bind(CallFilterUser)
    dp.filters_factory.bind(FilterForAskHowManyBlocks)
    dp.filters_factory.bind(FilterForGeneral)
    dp.filters_factory.bind(FilterForBattonsMenu)
    dp.filters_factory.bind(CallFilterForBattonsMenu)
    dp.filters_factory.bind(FilterForGuest)
    dp.filters_factory.bind(FilterForStart)
    dp.filters_factory.bind(CallFilterForError)
    dp.filters_factory.bind(CallFilterForGuest)
