from aiogram import types

from loader import dp
from utils.admin_utils import add_user, del_user
from utils.face_control import control
from utils.log import log
from work_vs_db.db_users import users_db


@dp.message_handler(commands=['adUser'])
async def adm_ad_user(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    all_users = users_db.users_names
    new_user = message.text[8:]
    answer = await add_user(new_user, all_users)
    await message.answer(answer)
    await log.write(f'admin: {answer}, ({message.from_user.username})')


@dp.message_handler(commands=['dlUser'])
async def adm_dell_user(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return
    all_users = users_db.users_names
    new_user = message.text[8:]
    answer = await del_user(new_user, all_users)
    await message.answer(answer)
    await log.write(f'admin: {answer}, ({message.from_user.username})')
