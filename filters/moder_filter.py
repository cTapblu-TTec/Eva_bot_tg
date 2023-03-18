from aiogram import Dispatcher
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS
from work_vs_db.db_moderators import moderators_db


class FilterModerAcces(BoundFilter):
    options = {'buttons': 'access_to_buttons_tools', 'files': 'access_to_files_tools',
               'groups': 'access_to_groups_tools', 'users': 'access_to_users_tools', 'state': 'access_to_state_tools'}

    def __init__(self, option, tool: str) -> None:
        self.option = self.options[option]
        self.tool = tool

    async def check(self, query):
        user_id = query.from_user.id
        if user_id in ADMINS:
            return True
        return await moderators_db.check_access_moderator(user_id, self.option, self.tool)


def registry_moder_filters(dp: Dispatcher):
    dp.filters_factory.bind(FilterModerAcces)
