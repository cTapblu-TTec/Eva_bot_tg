from contextlib import suppress
from asyncio import sleep, create_task

from aiogram.utils.exceptions import BadRequest

from loader import bot
from work_vs_db.db_users import users_db


async def delete_old_user_menu(chat_id: int, user_name: str):
    if users_db.users[user_name].menu_mess_id:
        menu_mess_id = users_db.users[user_name].menu_mess_id
        users_db.users[user_name].menu_mess_id = None
        await users_db.write(user_name, ['menu_mess_id'], ['None'])
        with suppress(BadRequest):
            create_task(bot.delete_message(chat_id=chat_id, message_id=menu_mess_id))


async def create_user_menu(chat_id: int, user_name: str, text: str, keyboard=None):
    await delete_old_user_menu(chat_id, user_name)
    if keyboard:
        msg = await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    else:
        msg = await bot.send_message(chat_id=chat_id, text=text)
    users_db.users[user_name].menu_mess_id = msg["message_id"]
    await users_db.write(user_name, ['menu_mess_id'], [msg["message_id"]])
    await delete_user_menu_after_time(chat_id, user_name)


async def delete_user_menu_after_time(_chat_id: int, _user_name: str, _time: int = 15):
    async def insert_def(chat_id, user_name, time):
        await sleep(60*time)  # ждем time минут
        await delete_old_user_menu(chat_id, user_name)

    create_task(insert_def(_chat_id, _user_name, _time))

