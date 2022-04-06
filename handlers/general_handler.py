from aiogram import types

from filters.chek_buttons import ChekButtons
from loader import dp
from utils.face_control import control
from utils.gena import gennadij
from utils.get_text import get_vk_text, get_template
from utils.log import log
from utils.notify_admins import notify
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


@dp.message_handler(ChekButtons())
async def work_buttons(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user == "guest": return

    button_name = message.text
    button = buttons_db.buttons[button_name]
    shablon = ''
    otmetki = ''
    gena = ''
    jopa = False

    # ШАБЛОН
    if button.shablon_file is not None and button.shablon_file != 'gena.txt':
        u = users_db.users[message.from_user.username]
        shablon, u.n_zamen, u.n_last_shabl = await get_template(u.n_zamen, u.n_last_shabl, button.shablon_file)

    # ГЕНА
    elif button.shablon_file == 'gena.txt':
        gena = await gennadij.get_text()

    # ОТМЕТКИ
    if button.work_file is not None:
        file_name = button.work_file
        try:
            f = f_db.files[file_name]
            # size_blok - сколько выдать отметок
            # button: name, work_file, num_block, size_blok, shablon_file, active
            # file: name, num_line, file_id, next_file_id
            otmetki, num_line, num_block = await get_vk_text(f.num_line, button.num_block, button.size_blok, f.name)
        except Exception:
            await notify(f'Файл {file_name} отсутствует в базе в таблице filess')
            jopa = True

    text = shablon + gena + otmetki
    if text: await message.answer(text)

    # если с отметками
    if button.work_file is not None and not jopa:
        await f_db.write(file_name, ['num_line'], [num_line])
        await buttons_db.write(button_name, ['num_block'], [num_block])
        await log(f'№ строки {message.text}: {f.num_line}, ({message.from_user.username})\n')
    else:
        await log(f'{message.text}, ({message.from_user.username})\n')  # пишем лог
    if button.hidden == 0:
        await stat_db.write(message.text, message.from_user.username)  # пишем статистику
