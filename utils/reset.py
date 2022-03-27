from data.config import LOG_CHAT
from loader import dp
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_stat import stat_db


async def reset_statistics():
    # NEW
    await stat_db.get_html()
    with open('statistic.html', 'rb') as file:
        await dp.bot.send_document(LOG_CHAT, file, caption='Статистика, счетчики сторис и шаблонов сброшены')
    for button in buttons_db.buttons_names:
        if buttons_db.buttons[button].num_block != -1:
            await buttons_db.write(button, ['num_block'], [1])
    await stat_db.dell()
    await stat_db.create(None)
