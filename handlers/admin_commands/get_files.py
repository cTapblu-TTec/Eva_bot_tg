from aiogram import types

from loader import dp
from utils.admin_utils import download_sended_file
from utils.log import log
from work_vs_db.db_filess import f_db


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def adm_change_file(message: types.Message):
    if message.document.file_name[:-4] in f_db.files_names:

        # -= ОТПРАВЛЯЕМ СТАРЫЙ ФАЙЛ:
        try:
            mess = f'Старая версия (использовано {f_db.files[message.document.file_name].num_line})'
            with open('dir_files/' + message.document.file_name, 'rb') as f:
                await message.reply_document(f, caption=mess)
        except FileNotFoundError:
            pass

        # -= СКАЧИВАЕМ НОВЫЙ ФАЙЛ:
        reply_mess, file_ok = await download_sended_file(message.document.file_id, message.document.file_name)
        if file_ok:
            await message.answer(reply_mess + f'\nКоманда для сброса:\n/set {message.document.file_name} num_line 0')
            await log.write(f'admin: Загружен файл - {message.document.file_name}, ({message.from_user.username})')
        else:
            await message.answer(reply_mess)
    else:
        await message.answer(f"Неверное имя файла, доступные имена: {str(f_db.files_names)}")
