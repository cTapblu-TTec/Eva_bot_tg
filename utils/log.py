from asyncio import sleep

from data.config import LOG_CHAT
from loader import dp


class Log:
    text = ''
    sended = True


async def log(text: str):
    if Log.sended:
        Log.sended = False
        Log.text += text  # накапливаем лог
        await sleep(60)  # ждем накопления лога 60 сек
        if Log.text and not Log.sended:
            await send()

    else:
        Log.text += text  # накапливаем лог
        if len(Log.text) > 1000:
            await send()


async def send():
    mess = Log.text  # это нужно чтобы очистить Лог как можно быстрее, для следующего запроса
    Log.text = ''  # очищаем лог
    Log.sended = True
    await dp.bot.send_message(LOG_CHAT, mess)  # отправляем лог
