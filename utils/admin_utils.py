from work_vs_db.db_buttons import buttons_db
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


async def del_user(new_user, all_users):
    new_user = new_user.strip()
    new_user = new_user.lstrip('@')
    if new_user in all_users:
        await users_db.write(new_user, 'dell_user', None)
        return f"Пользователь удален - {new_user}"
    else:
        return f"Пользователь не найден - {new_user}"
