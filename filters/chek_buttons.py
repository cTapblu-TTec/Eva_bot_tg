from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


from data.config import ADMINS
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db


class ChekButtons(BoundFilter):
    async def check(self, message: types.Message):
        if message.text in buttons_db.buttons_names and buttons_db.buttons[message.text].active == 1:
            return True
        return False


class ChekGroupButtons(BoundFilter):
    async def check(self, message: types.Message):
        group = message.text
        if group in buttons_db.buttons_groups:
            if groups_db.groups[group].hidden == 0:
                return True
            else:
                if str(message.from_user.id) in ADMINS:
                    return True
                if groups_db.groups[group].users and \
                        message.from_user.username in groups_db.groups[group].users:
                    return True
        return False


class CallChekGroupButtons(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'menu_groups':
                group = query[1]
                if group in buttons_db.buttons_groups:
                    if groups_db.groups[group].hidden == 0:
                        return True
                    else:
                        if str(callback.message.chat.id) in ADMINS:
                            return True
                        if groups_db.groups[group].users and \
                                callback.message.chat.username in groups_db.groups[group].users:
                            return True
                return True
        return False
