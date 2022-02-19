from aiogram import types

from data.config import ADMINS
from loader import dp
from work_vs_db.db_files import files_db
from work_vs_db.db_statistic import stat_db
from utils.get_text import s
from work_vs_db.db_vars import vars_db


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def download_doc(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        files = ['otmetki.txt', 'vk_id.txt', 'vk_club.txt', 'vk_lots.txt', 'vk_http.txt', 'polina.txt', 'name.txt']
        if message.document.file_name in files:
            vars = [vars_db.n_otmetki, vars_db.n_vk_id, vars_db.n_vk_club, vars_db.n_vk_lots, vars_db.n_vk_http, None, None]
            for i in range(len(files)):
                if message.document.file_name == files[i]:

                    file = open(message.document.file_name, 'rb')
                    # await dp.bot.send_document(int(admin), file)
                    if vars[i]:
                        await message.reply_document(file, caption = f'Старая версия (использовано {vars[i]})\nФайл заменен')
                    else: await message.reply_document(file, caption = f'Старая версия \nФайл заменен')
                    file.close()
                    await message.document.download(destination_file=message.document.file_name)
                    if message.document.file_name in ('otmetki.txt', 'polina.txt', 'name.txt'):
                        s.create_spiski((message.document.file_name, ))
                    await files_db.write(message.document.file_name, message.document.file_id)

        else:
            await message.reply(f"Неверное имя файла, доступные имена: {files}")
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.reply("Вы не админ этого бота, извините")
        return
