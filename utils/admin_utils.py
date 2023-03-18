from data.config import ADMIN_LOG_CHAT
from loader import bot
from utils.face_control import Guests
from utils.get_text import Files
from utils.log import log
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_files_id import files_id_db, download_file_from_tg
from work_vs_db.db_filess import f_db
from work_vs_db.db_stat import stat_db


async def get_button_clicks(button):
    file = buttons_db.buttons[button].work_file
    cliks = None
    if file is not None and file in f_db.files:
        length_file = await f_db.get_len_file(file)
        size = length_file - f_db.files[file].num_line
        if buttons_db.buttons[button].size_blok > 0:
            cliks = size // buttons_db.buttons[button].size_blok
    return cliks


async def download_sended_file(file_id, file_name):
    dir_f = 'dir_files/'
    reply_mess = ''
    try:
        file = await bot.get_file(file_id)
        await bot.download_file(file_path=file.file_path, destination=dir_f + file_name)

        with open(dir_f + file_name, 'r', encoding='utf-8') as f:
            length = len(f.readlines())  # проверяем что файл читается
        if length > 20000:
            reply_mess += 'Файл очень большой, бот будет тормозить, рекомендуемый размер - 10000 строк'
        # сохраняем новый id файла
        await files_id_db.write(file_name, file_id)
        # сохраняем длину файла
        if file_name not in f_db.files:
            await f_db.write(file_name, 'add_file', '')
            await log.write(f"admin: файл '{file_name}' добавлен в базу")
        await f_db.write(file_name, ['length'], [length])
        # удаляем файл из пяти файлов в памяти
        if file_name in Files: Files.pop(file_name)
        return reply_mess, True

    except (SyntaxError, UnicodeError):
        reply_mess += 'Не удалось прочесть новый файл, проверьте кодировку'
        await download_file_from_tg(file_name)  # скачиваем обратно старый файл
        return reply_mess, False


async def reset_statistics():
    await stat_db.get_html()
    with open('statistic.html', 'rb') as file:
        await bot.send_document(ADMIN_LOG_CHAT, file, caption='Статистика')

    await stat_db.get_html(get_all=True, file_stat='all_butt_stat.html')
    with open('all_butt_stat.html', 'rb') as file:
        await bot.send_document(ADMIN_LOG_CHAT, file, caption='Статистика и счетчики сторис (блоков) сброшены')

    await stat_db.dell()
    await stat_db.create(None)
    await buttons_db.reset_buttons_num_blocks()
    Guests.guests = {}


def get_key_by_value(dic, val):
    for i in dic:
        if dic[i] == val:
            return i
    return None


def good_format(text: str):
    if text and ',' in text:
        _list = text.split(',')
        new_list = []
        for i in _list:
            i = i.strip()
            if i:
                new_list.append(i)
        text = ",".join(new_list)
    return text
