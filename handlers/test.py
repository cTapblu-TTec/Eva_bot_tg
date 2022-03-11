from aiogram import types
from datetime import datetime

import utils.get_text
from data.config import ADMINS
from loader import dp
from work_vs_db.db_statistic import stat_db
from work_vs_db.db_users import users_db
from work_vs_db.db_vars import vars_db




@dp.message_handler(commands=['test'])
async def ad_rs(message: types.Message):

    if str(message.from_user.id) in ADMINS:

        print(vars_db.n_otmetki, vars_db.n_storis, vars_db.n_shablon)

        #u = await users_db.read('n_zamen, n_last_otm, n_last_sabl', 'cTapblu_TTec')
        #print(u.n_zamen)

        # await vars_db.write(['n_otmetki', 'n_storis', 'n_shablon'], [12,75,2])
        # print(vars_db.n_otmetki, vars_db.n_storis, vars_db.n_shablon)


        #await users_db.write('cTapblu_TTec', ['n_last_otm', 'n_zamen', 'n_last_sabl'], [5, 4, (3, 2)])
        #z = await users_db.read('', 'cTapblu_TTec')
        #print(z)

    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.reply("Вы не админ этого бота, извините")
