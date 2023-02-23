from dataclasses import dataclass

from data.config import ADMINS
from work_vs_db.db_users import users_db


@dataclass()
class Guests:
    guests = {}


async def control(user_id: int, user_name: str):
    user = "guest"
    if user_id in ADMINS:
        user = "admin"  # присвоить статус админ

    elif user_name in users_db.users_names:
        user = "user"  # присвоить статус юзер

    else:  # user = "guest"
        Guests.guests[user_id] = user_name
    return user
