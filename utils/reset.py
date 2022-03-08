from data.config import LOG_CHAT
from loader import dp
from work_vs_db.db_statistic import stat_db
from work_vs_db.db_vars import vars_db


async def reset_statistics():
    await stat_db.get_html()
    file = open('statistic.html', 'rb')
    await dp.bot.send_document(LOG_CHAT, file, caption='Статистика, счетчики сторис и шаблонов сброшены')
    file.close()

    await vars_db.write(['n_storis', 'n_shablon'], [1, 0])
    await stat_db.clear()
