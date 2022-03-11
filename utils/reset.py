from data.config import LOG_CHAT
from loader import dp
from work_vs_db.db_statistic import stat_db
from work_vs_db.db_vars import vars_db


async def reset_statistics():
    await stat_db.get_html()
    file = open('statistic.html', 'rb')
    await dp.bot.send_document(LOG_CHAT, file, caption='Статистика, счетчики сторис и шаблонов сброшены')
    file.close()

    await vars_db.write(['n_storis', 'n_shablon', 'n_get_id', 'n_get_http', 'n_get_club', 'n_get_lots', 'n_siti_get'],
                        [1, 0, 1, 1, 1, 1, 1])
    await stat_db.clear()
