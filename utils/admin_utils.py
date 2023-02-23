from loader import bot
from utils.get_text import Files
from utils.log import log
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_files_id import files_id_db, download_file_from_tg
from work_vs_db.db_filess import f_db
from work_vs_db.db_users import users_db


async def get_button_clicks(button):
    file = buttons_db.buttons[button].work_file
    cliks = None
    if file is not None and file in f_db.files:
        if f_db.files[file].length is None:
            try:
                with open('dir_files/' + file, "r", encoding='utf-8') as f:
                    len_ = len(f.readlines())
                await f_db.write(file, ['length'], [len_])
            except FileNotFoundError:
                return f'файл {file} не найден'
        size = f_db.files[file].length - f_db.files[file].num_line
        if buttons_db.buttons[button].size_blok >= 1:
            cliks = size // buttons_db.buttons[button].size_blok
    return cliks


async def add_user(new_user, all_users):
    new_user = new_user.strip()
    new_user = new_user.lstrip('@')
    iskl = ' !"$%&()*+,/:;<>=?@^#{}|~'
    begin = True
    for i in iskl:
        if i in new_user:
            begin = False
    if new_user == '':
        begin = False
    if new_user.isascii() and begin:
        if new_user in all_users:
            return f"Пользователь {new_user} уже был в списке"
        await users_db.write(new_user, 'add_user', None)
        return f"Добавлен пользователь - {new_user}"

    else:
        return f"Неверный формат - {new_user}"


async def del_user(user, all_users):
    user = user.strip()
    user = user.lstrip('@')
    if user in all_users:
        await users_db.write(user, 'dell_user', None)
        return f"Пользователь удален - {user}"
    else:
        return f"Пользователь не найден - {user}"


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
