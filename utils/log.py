from asyncio import sleep, create_task

from data.config import LOG_CHAT
from loader import dp


class Log:
    text = ''
    sended = True

    async def write(self, text: str):
        if text[:-1] != '\n':
            text += '\n'
        self.text += text  # накапливаем лог
        if self.sended:
            self.sended = False
            create_task(self.wait())
        else:
            if len(self.text) > 1000:
                await self.send()

    async def wait(self):
        await sleep(60)  # ждем накопления лога 60 сек
        if self.text and not self.sended:
            await self.send()

    async def send(self):
        mess = self.text  # это нужно чтобы очистить Лог как можно быстрее, для следующего запроса
        self.text = ''  # очищаем лог
        self.sended = True
        await dp.bot.send_message(LOG_CHAT, mess)  # отправляем лог


log = Log()
