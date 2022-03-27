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
        await stat_db.write('Гость', message.from_user.username)
        await log(f'{message.text}, ({message.from_user.username})\n')
        return user

    return user
