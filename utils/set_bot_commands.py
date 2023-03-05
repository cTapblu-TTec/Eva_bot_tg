import logging

from aiogram import types

from loader import bot
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db


async def set_default_commands():
    commands = [types.BotCommand("start", "главное меню")]

    for group in buttons_db.buttons_groups:
        if groups_db.groups[group].hidden == 0:  # если не скрытая группа
            commands.append(types.BotCommand(groups_db.groups[group].en_name, groups_db.groups[group].specification))

    try:
        await bot.set_my_commands(commands)
    except Exception:
        logging.error(f"Команды не установились \n{commands=}")
