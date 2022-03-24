from aiogram import types

from loader import dp
from utils.Proverka import prover
from utils.get_text import get_vk_text, Vid_Shabl
from utils.log import log
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
# РАБОТА С ФАЙЛАМИ
from work_vs_db.db_users import users_db


@dp.message_handler(text=buttons_db.buttons_names)
async def stor(message: types.Message):
    user = await prover(message, message.text)  # проверяем статус пользователя и пишем статистику
    if user == "guest": return

    button_name = message.text
    button = buttons_db.buttons[button_name]
    shablon = ''
    otmetki = ''

    # ОТМЕТКИ
    if button.work_file is not None:
        file_name = button.work_file
        f = f_db.files[file_name]

        # size_blok - сколько выдать отметок
        # button: name, work_file, num_block, size_blok, shablon_file, active
        # file: name, num_line, num_block, size_blok, file_id, next_file_id
        otmetki, num_line, num_block = await get_vk_text(f.num_line, button.num_block, button.size_blok, f.name)

    # ШАБЛОН
    if button.shablon_file is not None:
        u = users_db.users[message.from_user.username]
        shablon, u.n_zamen, u.n_last_shabl = \
            await Vid_Shabl(u.n_zamen, u.n_last_shabl)  # получаем шаблон
    text = shablon + otmetki

    await message.answer(text)

    if button.work_file is not None:
        await f_db.write(file_name, ['num_line'], [num_line])
        await buttons_db.write(button_name, ['num_block'], [num_block])
        await log(f'№ строки {message.text}: {f.num_line}, ({message.from_user.username})\n')
    else:
        await log(f'{message.text}, ({message.from_user.username})\n')
