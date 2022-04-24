from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db


class ChekButtons(BoundFilter):
    async def check(self, message: types.Message):
        if message.text in buttons_db.buttons_names:
            return True
        return False


class ChekGroupButtons(BoundFilter):
    async def check(self, message: types.Message):
        if message.text in buttons_db.buttons_groups:
            if groups_db.groups[message.text].hidden == 0:
                return True
            else:
                if str(message.from_user.id) in ADMINS:
                    return True
                if groups_db.groups[message.text].users and \
                        message.from_user.username in groups_db.groups[message.text].users:
                    return True
        return False
