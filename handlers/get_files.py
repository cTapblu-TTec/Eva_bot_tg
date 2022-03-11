from aiogram import types

from data.config import ADMINS
from loader import dp
from utils.log import log
from work_vs_db.db_files import files_db, download
from work_vs_db.db_statistic import stat_db
from utils.get_text import s
from work_vs_db.db_vars import vars_db


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def download_doc(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        files = ['otmetki.txt', 'vk_id.txt', 'vk_club.txt', 'vk_lots.txt', 'vk_http.txt', 'polina.txt', 'name.txt']
        if message.document.file_name in files:  # если файл с правильным именем
            vars_ = [vars_db.n_otmetki, vars_db.n_vk_id, vars_db.n_vk_club, vars_db.n_vk_lots, vars_db.n_vk_http, None,
                     None]
            for i in range(len(files)):
                if message.document.file_name == files[i]:

                    # -= ОТПРАВЛЯЕМ СТАРЫЙ ФАЙЛ:
                    # await dp.bot.send_document(int(admin), file)
                    if vars_[i]:
                        with open(message.document.file_name, 'rb') as f:
                            await message.reply_document(f,
                                                         caption=f'Старая версия (использовано {vars_[i]})\nФайл заменен')
                    else:
                        with open(message.document.file_name, 'rb') as f:
                            await message.reply_document(f, caption='Старая версия \nФайл заменен')

                    # -= СКАЧИВАЕМ НОВЫЙ ФАЙЛ:
                    try:
                        await message.document.download(destination_file=message.document.file_name)
                        with open(message.document.file_name, 'r') as f:
                            f.readline()  # проверяем что файл читается
                        await files_db.write(message.document.file_name,
                                             message.document.file_id)  # сохраняем новый id файла
                        if message.document.file_name in ('otmetki.txt', 'polina.txt', 'name.txt'):
                            s.create_spiski((message.document.file_name,))

                        await log(f'admin: Заменен файл - {message.document.file_name}, '
                                  f'({message.from_user.username}\n')

                    except Exception:
                        await message.reply('Не удалось прочесть новый файл, файл не заменен, возвращен старый, '
                                            'проверьте кодировку')
                        await download(message.document.file_name)  # скачиваем обратно старый файл

        else:
            await message.reply(f"Неверное имя файла, доступные имена: {files}")
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.reply("Вы не админ этого бота, извините")
        return
