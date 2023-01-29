from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_users import users_db


class MenuMid(BaseMiddleware):

    async def on_pre_process_message(self, msg: Message, data: dict):
        if isinstance(msg.text, str) and msg.from_user.username in users_db.users:
            if msg.text[:1] == '/' and msg.text[1:] in groups_db.en_names_groups:
                msg.text = msg.text[1:]
                for gr in groups_db.groups:
                    if groups_db.groups[gr].en_name == msg.text:
                        msg.text = gr

            if msg.text == 'Назад':
                if users_db.users[msg.from_user.username].menu != '':
                    msg.text = users_db.users[msg.from_user.username].menu
                else:
                    msg.text = '/del'


"""class PrivateMid(BaseMiddleware):

    async def on_pre_process_message(self, msg: Message, data: dict):

        if msg.chat['type'] != "private":
            msg.text = "/not_private"
"""