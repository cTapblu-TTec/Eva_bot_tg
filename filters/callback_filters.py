from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_groups_buttons import groups_db


# --== КНОПКИ ==--
class ChekButtonsForCallback(BoundFilter):
    async def check(self,  callback: types.CallbackQuery):
        if callback.data in buttons_db.buttons_names:
            return True
        return False


class ChekDellButton(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if callback.data[:11] == 'dell_button':
            return True
        return False


# --== ГРУППЫ ==--
class ChekGroupsForCallback(BoundFilter):
    async def check(self,  callback: types.CallbackQuery):
        if callback.data in groups_db.groups:
            return True
        return False


# todo попробовать сделать для разных хендлеров - if data['filter'] == 'параметр из хендлера'
class CallbackGroupValueFilter(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'gr_value':
                return True
        return False


class ChekDellGroup(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if '/' in callback.data[1:]:
            query = callback.data.split('/')
            if query[0] == 'dell_group':
                return True
        return False


# --== ФАЙЛЫ ==--
class ChekFilesForCallback(BoundFilter):
    async def check(self,  callback: types.CallbackQuery):
        if callback.data in f_db.files:
            return True
        return False
