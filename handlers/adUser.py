from aiogram import types

from data.config import ADMINS
from loader import dp
from utils.log import log
from work_vs_db.db_statistic import stat_db
from work_vs_db.db_users import users_db


@dp.message_handler(commands=['adUser'])
async def adu(message: types.Message):
    if str(message.from_user.id) in ADMINS:

        users = users_db.users_names
        text = message.text[8:]
        text = text.strip()
        text = text.lstrip('@')
        iskl = ' !"$%&()*+,/:;<>=?@^#{}|~'
        begin = True
        for i in iskl:
            if i in text:
                begin = False
        if text == '': begin = False
        if text.isascii() and begin:
            if text in users:
                await message.reply("Пользователь уже был в списке")
                return
            await users_db.write(text, 'add_user', None)

            await message.reply("Добавлен пользователь - " f"{text}")
            await log(f'admin: Добавлен пользователь - {text}, ({message.from_user.username} - /adUser)\n')


        else:
            await message.reply("Неверный формат - " f"{text}")
            return

    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.reply("Вы не админ этого бота, извините")
        return


@dp.message_handler(commands=['dlUser'])
async def dlu(message: types.Message):
    if str(message.from_user.id) in ADMINS:

        users = users_db.users_names
        text = message.text[8:]
        text = text.strip()
        text = text.lstrip('@')
        if text in users:
            await users_db.write(text, 'dell_user', None)
            await message.reply("Пользователь удален - " f"{text}")
            await log(f'admin: Пользователь удален - {text}, ({message.from_user.username} - /dlUser)\n')

        else:
            await message.reply("Пользователь не найден - " f"{text}")

    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.reply("Вы не админ этого бота, извините")
        return
