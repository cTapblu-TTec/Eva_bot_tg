from asyncio import create_task

from aiogram import types
# from app import logger
from filters.chek_buttons import ChekButtons
from loader import dp
from utils.face_control import control
from utils.gena import gennadij
from utils.get_text import get_link_list, get_template
from utils.log import log
from utils.notify_admins import notify
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


@dp.message_handler(ChekButtons())
async def work_buttons(message: types.Message):
    # logger.info("1 - Start handler")
    user = await control(message)  # проверяем статус пользователя
    if user == "guest": return

    button_name = message.text
    button = buttons_db.buttons[button_name]
    username = message.from_user.username
    template = ''
    links = ''
    number = ''
    otm = False
    num = False
    tem = False
    users_db.users[username].last_button = button_name
    u = users_db.users[username]

    # logger.info("2 - Номер блока")

    # НОМЕР БЛОКА todo имя блока без номера
    if button.num_block != -1:
        if button.name_block is not None:
            number = f'{button.num_block} {button.name_block}\n'
        else:
            number = f'{button.num_block}\n'
        buttons_db.buttons[button_name].num_block += 1
        num = True
    # logger.info("3 - Шаблон")

    # ШАБЛОН
    if button.shablon_file is not None and button.shablon_file != 'gena.txt':
        template, u.n_zamen, u.n_last_shabl = await get_template(u.n_zamen, u.n_last_shabl, button.shablon_file)
        users_db.users[username].n_zamen = u.n_zamen
        users_db.users[username].n_last_shabl = u.n_last_shabl
        tem = True
    # ГЕНА
    elif button.shablon_file == 'gena.txt':
        template = await gennadij.get_text()

    # logger.info("4 - Отметки")

    # ОТМЕТКИ
    if button.work_file is not None:
        try:
            num_line = f_db.files[button.work_file].num_line
            file = f_db.files[button.work_file].name
            links, num_line = await get_link_list(num_line, button.size_blok, file, button_name)
            otm = True
            f_db.files[button.work_file].num_line = num_line
        except Exception:
            await notify(f'Файл {button.work_file} отсутствует в базе в таблице filess')

    # logger.info("5 - Клавиатура")

    # КЛАВИАТУРА
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Назад', button_name])

    # ВЫДАЧА БЛОКА

    # logger.info("6 - Выдача блока")

    text = number + template + links
    if text: create_task(message.answer(text, reply_markup=keyboard))

    # logger.info("7 - Начало записи в БД")

    # ПОСЛЕ ВЫДАЧИ БЛОКА - запись в базы, лог, статистику
    if num:  # если с номером
        await buttons_db.write(button_name, 'n_block', buttons_db.buttons[button_name].num_block)

    # -----===== исправить на работу без Ф-строк========-------
    if tem:  # если с шаблоном
        await users_db.write(username, ['n_zamen', 'n_last_shabl', 'last_button'],
                             [u.n_zamen, u.n_last_shabl, button_name])
    else:  # клавиатура
        await users_db.write(username, ['last_button'], [button_name])

    if button.hidden == 0:  # пишем статистику если кнопка не скрытая
        await stat_db.write(button_name, username)

    if otm:  # если с отметками
        await f_db.write(button.work_file, 'n_line', f_db.files[button.work_file].num_line)
        await log.write(f'{button_name}, № строки {f_db.files[button.work_file].num_line}, ({username})\n')
        # logger.info("8 - Конец")
    else:
        await log.write(f'{button_name}, ({username})\n')
