from aiogram import types
from data.config import ADMINS
from work_vs_db.db_statistic import stat_db
from work_vs_db.db_users import users_db


async def prover(message: types.Message, command):
    user = "guest"
    if str(message.from_user.id) in ADMINS:
        user = "admin"  # присвоить статус админ

    elif message.from_user.username in users_db.users_names:
        user = "user"  # присвоить статус юзер

    else:
        await message.answer("Извините, у Вас нет доступа к боту")
    await stat_db.write(command, message.from_user.username)  # пишем статистику
    return user

