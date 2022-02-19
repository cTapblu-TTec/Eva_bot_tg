import logging

from loader import dp
from data.config import ADMINS


async def on_startup_notify():
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот запущен, /admin")
        except Exception as err:
            logging.exception(err)


# функция уведомления админов сообщением mess
async def notify(mess):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, mess)
        except Exception as err:
            logging.exception(err)

"""
async def on_shutdown_notify(dp: Dispatcher):
    for admin in ADMINS:
        await dp.bot.send_message(admin, "Бот выключен")
        file = open('settings.txt', 'rb')
        await dp.bot.send_document(-745165011, file)
        file.close()

"""
