import asyncio

from aiogram import types

from loader import dp
from utils.face_control import control
from utils.get_text import Files
from utils.log import log
from work_vs_db.db_files_id import files_id_db, download
from work_vs_db.db_filess import f_db


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def adm_change_file(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return
    if message.document.file_name[:-4] in f_db.files_names:
        dir_f = 'dir_files/'

        # -= ОТПРАВЛЯЕМ СТАРЫЙ ФАЙЛ:
        # await dp.bot.send_document(int(admin), file)
        try:
            with open(dir_f + message.document.file_name, 'rb') as f:
                await message.reply_document(f, caption='Старая версия (использовано '
                                                        f'{f_db.files[message.document.file_name].num_line})'
                                                        '\nФайл заменен')
        except FileNotFoundError:
            await message.reply('Файл загружен')
            asyncio.create_task(log(f'admin: Старый файл не найден - '
                                    f'{message.document.file_name}, ({message.from_user.username})\n'))

        # -= СКАЧИВАЕМ НОВЫЙ ФАЙЛ:
        try:
            await message.document.download(destination_file=dir_f + message.document.file_name)
            with open(dir_f + message.document.file_name, 'r', encoding='utf-8') as f:
                length = len(f.readlines())  # проверяем что файл читается
            if length > 20000:
                await message.reply('Файл очень большой, бот будет тормозить, рекомендуемый размер - 10000 строк')
            # сохраняем новый id файла
            await files_id_db.write(message.document.file_name, message.document.file_id)
            # сохраняем длину файла
            await f_db.write(message.document.file_name, ['length'], [length])
            # удаляем файл из пяти файлов в памяти
            if message.document.file_name in Files:
                Files.pop(message.document.file_name)

            await message.reply(f'Команда для сброса:\n/set {message.document.file_name} num_line 0')
            await log.write(f'admin: Загружен файл - {message.document.file_name}, '
                      f'({message.from_user.username})\n')

        except (SyntaxError, UnicodeError):
            await message.reply('Не удалось прочесть новый файл, файл не заменен, возвращен старый, '
                                'проверьте кодировку')
            await download(message.document.file_name)  # скачиваем обратно старый файл

    else:
        await message.reply(f"Неверное имя файла, доступные имена: {str(f_db.files_names)}")
