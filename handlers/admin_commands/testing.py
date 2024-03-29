from aiogram import types

from app import logger
from filters.admin_filters import FilterCheckAdmin
from loader import dp

from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_moderators import moderators_db
from work_vs_db.db_users import users_db


@dp.message_handler(FilterCheckAdmin(), commands=['test'])
async def test(message: types.Message):
    async def check(db, buff, name_item, text):
        all_good = True
        for item in buff:
            for db_i in db:
                if db_i[name_item] == item:
                    for key in db_i:
                        # print(item, key, db_i[key], getattr(buff[item], key, None))
                        if db_i[key] != getattr(buff[item], key, None) and key != 'n_last_shabl':
                            logger.warning(f"test: {item}|{key}|{db_i[key]}|{getattr(buff[item], key, None)}")
                            text += f"test: {item}|{key}|{db_i[key]}|{getattr(buff[item], key, None)}\n"
                            all_good = False
        return all_good, text

    t = ''
    b, t = await check(await buttons_db.get_all_from_bd(), buttons_db.buttons, 'name', t)
    g, t = await check(await groups_db.get_all_from_bd(), groups_db.groups, 'name', t)
    f, t = await check(await f_db.get_all_from_bd(), f_db.files, 'name', t)
    u, t = await check(await users_db.get_all_from_bd(), users_db.users, 'user_name', t)
    m, t = await check(await moderators_db.get_all_from_bd(), moderators_db.moderators, 'moderator_id', t)
    a, t = await check(await adm_chats_db.get_all_from_bd(), adm_chats_db.chats, 'chat_id', t)

    answer = ''
    if b:
        answer += "\nКнопки - Ок"
    else:
        answer += "\nКнопки - Fail"

    if g:
        answer += "\nГруппы - Ок"
    else:
        answer += "\nГруппы - Fail"

    if f:
        answer += "\nФайлы - Ок"
    else:
        answer += "\nФайлы - Fail"

    if u:
        answer += "\nПользователи - Ок"
    else:
        answer += "\nПользователи - Fail"

    if m:
        answer += "\nМодераторы - Ок"
    else:
        answer += "\nМодераторы - Fail"

    if a:
        answer += "\nАдминскиеЧаты - Ок"
    else:
        answer += "\nАдминскиеЧаты - Fail"

    await message.answer(answer)
    if t:
        await message.answer(t)
