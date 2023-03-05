from asyncio import sleep, create_task

from data.config import LOG_CHAT, ADMIN_LOG_CHAT
from loader import bot


async def resise_text(text: str):
    list_text = text.split('\n')
    related_lines = {}
    num_line = -1
    for line in list_text:
        num_line += 1
        num_num = line.rfind(' ') + 1
        if line[num_num:].isdigit():
            if related_lines.get(line[:num_num]):
                related_lines[line[:num_num]].append(num_line)
            else:
                related_lines[line[:num_num]] = [num_line]
        else:
            if related_lines.get(line):
                related_lines[line].append(num_line)
            else:
                related_lines[line] = [num_line]
    text = ''
    for line in related_lines:
        if line:
            x = len(related_lines[line])
            if x > 1:
                text += str(x) + 'х - '
            text += list_text[related_lines[line][-1]] + '\n'
    return text


class Log:
    text = {}

    async def write(self, text: str, user='user'):
        if 'admin' in text[:7] or user == 'admin':
            await self.write_log('admin', text)
        else:
            await self.write_log(user, text)

    async def write_log(self, user, text):
        text += '\n\n'
        if self.text.get(user):
            self.text[user] += text  # накапливаем лог
            if len(self.text[user]) > 1000:
                await self.send(user)
        else:
            self.text[user] = text
            create_task(self.wait(user))

    async def wait(self, user):
        if user == 'admin':
            await sleep(1)
        else:
            await sleep(60)  # ждем накопления лога 60 сек
        if self.text[user]:
            await self.send(user)

    async def send(self, user):
        mess = self.text[user]  # это нужно чтобы очистить Лог как можно быстрее, для следующего запроса
        self.text.pop(user)
        if user == 'admin':
            await bot.send_message(ADMIN_LOG_CHAT, mess)
        else:
            mess = await resise_text(mess)
            await bot.send_message(LOG_CHAT, user + ":\n" + mess)

    async def send_log_now(self):
        for user in self.text:
            mess = self.text[user]
            if user == 'admin':
                await bot.send_message(ADMIN_LOG_CHAT, mess)
            else:
                mess = await resise_text(mess)
                await bot.send_message(LOG_CHAT, '• ' + user + ":\n" + mess)
        self.text = {}


log = Log()
