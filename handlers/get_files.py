from aiogram import types

from loader import dp
from utils.Proverka import prover
from utils.log import log
from work_vs_db.db_files import files_db, download
from work_vs_db.db_filess import f_db


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def adm_change_file(message: types.Message):
    user = await prover(message, message.text)  # проверяем статус пользователя и пишем статистику
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return
    if message.document.file_name[:-4] in f_db.files_names:
        dir = 'dir_files/'

        # -= ОТПРАВЛЯЕМ СТАРЫЙ ФАЙЛ:
        # await dp.bot.send_document(int(admin), file)
        try:
            with open(dir+message.document.file_name, 'rb') as f:
                await message.reply_document(f, caption='Старая версия (использовано '
                                                        f'{f_db.files[message.document.file_name].num_line})'
                                                        '\nФайл заменен')
        except Exception:
            await log(f'admin: Старый файл не найден - {message.document.file_name}, ({message.from_user.username})\n')
            await message.reply('Файл загружен')

        # -= СКАЧИВАЕМ НОВЫЙ ФАЙЛ:
        try:
            await message.document.download(destination_file=dir+message.document.file_name)
            with open(dir+message.document.file_name, 'r') as f:
                length = len(f.readlines())  # проверяем что файл читается
            if length > 20000:
                await message.reply('Файл очень большой, бот будет тормозить, рекомендуемый размер - 10000 строк')
            await files_db.write(message.document.file_name,
                                 message.document.file_id)  # сохраняем новый id файла

            await f_db.write(message.document.file_name, ['file_id', 'length'], [message.document.file_id, length])

            await log(f'admin: Заменен файл - {message.document.file_name}, '
                      f'({message.from_user.username})\n')

        except Exception:
            await message.reply('Не удалось прочесть новый файл, файл не заменен, возвращен старый, '
                                'проверьте кодировку')
            await download(message.document.file_name)  # скачиваем обратно старый файл

    else:
        await message.reply(f"Неверное имя файла, доступные имена: {str(f_db.files_names)}")
