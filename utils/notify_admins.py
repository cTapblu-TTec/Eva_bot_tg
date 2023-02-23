from asyncio import create_task

from loader import bot
from data.config import ADMINS, LOG_CHAT


async def on_startup_notify():
    await bot.send_message(LOG_CHAT, 'Бот запущен')


# функция уведомления админов сообщением mess
async def notify(mess):
    for admin in ADMINS:
        create_task(bot.send_message(admin, mess))
