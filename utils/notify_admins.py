from asyncio import create_task

from loader import bot
from data.config import ADMINS, ADMIN_LOG_CHAT


async def on_startup_notify():
    await bot.send_message(ADMIN_LOG_CHAT, 'Бот запущен')
    # await notify_admins('Бот запущен')


# функция уведомления админов сообщением mess
async def notify_admins(mess):
    for admin in ADMINS:
        create_task(bot.send_message(admin, mess))
