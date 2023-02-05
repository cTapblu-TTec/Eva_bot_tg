from asyncio import create_task

from loader import dp
from data.config import ADMINS, LOG_CHAT


async def on_startup_notify():
    await dp.bot.send_message(LOG_CHAT, 'Бот запущен')


# функция уведомления админов сообщением mess
async def notify(mess):
    for admin in ADMINS:
        create_task(dp.bot.send_message(int(admin), mess))
