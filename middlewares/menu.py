from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from data.config import ADMINS
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_users import users_db


class MenuMid(BaseMiddleware):
    async def on_pre_process_message(self, msg: Message, data: dict):
        is_admin = msg.chat.id in ADMINS
        # Меняет английские названия групп на русские
        if isinstance(msg.text, str) and (msg.from_user.username in users_db.users or is_admin):
            if msg.text[:1] == '/' and msg.text[1:] in groups_db.en_names_groups:
                msg.text = msg.text[1:]
                for gr in groups_db.groups:
                    if groups_db.groups[gr].en_name == msg.text:
                        msg.text = gr
