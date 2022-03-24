from loader import dp
from data.config import ADMINS, LOG_CHAT


async def on_startup_notify():
    await dp.bot.send_message(LOG_CHAT, 'Бот запущен')


# функция уведомления админов сообщением mess
async def notify(mess):
    for admin in ADMINS:
        await dp.bot.send_message(admin, mess)

