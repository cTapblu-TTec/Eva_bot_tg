from data.config import ADMINS
from loader import dp
from utils.log import log
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


async def control(user_id: int, name: str, text: str = ""):
    user = "guest"

    if str(user_id) in ADMINS:
        user = "admin"  # присвоить статус админ

    elif name in users_db.users_names:
        user = "user"  # присвоить статус юзер

    else:  # user = "guest"
        await dp.bot.send_message(user_id, "Извините, у Вас нет доступа к боту")
        if name is not None:
            username = f'{name} ({user_id})'
        else:
            username = user_id
        await stat_db.write('Гость', username)
        await log.write(f'Гость: "{text}", ({username})\n')
    return user
