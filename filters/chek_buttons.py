from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from work_vs_db.db_buttons import buttons_db


class ChekButtons(BoundFilter):
    async def check(self, message: types.Message):
        if message.text in buttons_db.buttons_names:
            return True
        return False


class ChekGroupButtons(BoundFilter):
    async def check(self, message: types.Message):
        if message.text in buttons_db.buttons_groups:
            return True
        return False
