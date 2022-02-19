from asyncio import sleep

from data.config import LOG_CHAT
from loader import dp


class Log:
    text = ''


async def log(text: str):
    if Log.text == '':
        Log.text += text  # накапливаем лог
        await sleep(60)  # ждем накопления лога 60 сек
        await dp.bot.send_message(LOG_CHAT, Log.text)  # отправляем лог
        Log.text = ''  # очищаем лог
    else:
        Log.text += text  # только накапливаем лог
