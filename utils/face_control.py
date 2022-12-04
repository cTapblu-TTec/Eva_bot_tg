from aiogram import types
from data.config import ADMINS
from utils.log import log
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


async def control(message: types.Message):
    user = "guest"

    if str(message.from_user.id) in ADMINS:
        user = "admin"  # присвоить статус админ

    elif message.from_user.username in users_db.users_names:
        user = "user"  # присвоить статус юзер

    else:  # user = "guest"
        await message.answer("Извините, у Вас нет доступа к боту")
        if message.from_user.username is not None:
            username = message.from_user.username
        elif message.from_user.first_name is not None:
            username = message.from_user.first_name
            if message.from_user.last_name is not None:
                username += '_' + message.from_user.last_name
        else:
            username = message.from_user.id
        await stat_db.write('Гость', username)
        await log(f'Гость: "{message.text}", ({username})\n')

    return user
