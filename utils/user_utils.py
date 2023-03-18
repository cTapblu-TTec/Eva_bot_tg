from contextlib import suppress
from asyncio import sleep, create_task

from aiogram.utils.exceptions import BadRequest

from loader import bot
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_users import users_db


async def delete_old_user_menu(chat_id: int, user_name: str):
    async def del_mess(c_id, m_id):
        with suppress(BadRequest):
            await bot.delete_message(chat_id=c_id, message_id=m_id)

    if users_db.users[user_name].menu_mess_id:
        menu_mess_id = users_db.users[user_name].menu_mess_id
        users_db.users[user_name].menu_mess_id = None
        await users_db.write(user_name, ['menu_mess_id'], ['None'])
        create_task(del_mess(c_id=chat_id, m_id=menu_mess_id))


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


async def button_is_available(butt, user):
    is_available_user = False
    button_in_available_group = False
    list_available_grous = []
    for group in groups_db.groups:
        if groups_db.groups[group].hidden == 0 or \
                (groups_db.groups[group].users and user in groups_db.groups[group].users):
            list_available_grous.append(group)
    for group in list_available_grous:
        if buttons_db.buttons[butt].group_buttons and group in buttons_db.buttons[butt].group_buttons:
            button_in_available_group = True
    if buttons_db.buttons[butt].hidden == 0 or \
            (buttons_db.buttons[butt].users and user in buttons_db.buttons[butt].users):
        is_available_user = True
    if button_in_available_group and is_available_user:
        return True
    else:
        return False
