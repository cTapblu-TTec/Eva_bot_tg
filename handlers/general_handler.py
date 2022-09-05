from aiogram import types

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
    user = await control(message)  # проверяем статус пользователя
    if user == "guest": return

    button_name = message.text
    button = buttons_db.buttons[button_name]
    template = ''
    links = ''
    number = ''
    otm = False
    num = False
    tem = False
    u = users_db.users[message.from_user.username]

    # НОМЕР БЛОКА
    if button.num_block != -1:
        if button.name_block is not None:
            number = f'{button.num_block} {button.name_block}\n'
        else:
            number = f'{button.num_block}\n'
        button.num_block += 1
        num = True

    # ШАБЛОН
    if button.shablon_file is not None and button.shablon_file != 'gena.txt':
        template, u.n_zamen, u.n_last_shabl = await get_template(u.n_zamen, u.n_last_shabl, button.shablon_file)
        tem = True
    # ГЕНА
    elif button.shablon_file == 'gena.txt':
        template = await gennadij.get_text()

    # ОТМЕТКИ
    if button.work_file is not None:
        try:
            num_line = f_db.files[button.work_file].num_line
            file = f_db.files[button.work_file].name
            links, num_line = await get_link_list(num_line, button.size_blok, file)
            otm = True
        except Exception:
            await notify(f'Файл {button.work_file} отсутствует в базе в таблице filess')

    # КЛАВИАТУРА
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Назад', button_name])
    await users_db.write(message.from_user.username, ['last_button'], [button_name])

    # ВЫДАЧА БЛОКА
    text = number + template + links
    if text: await message.answer(text, reply_markup=keyboard)

    # ПОСЛЕ ВЫДАЧИ БЛОКА - запись в базы, лог, статистику
    if num:  # если с номером
        await buttons_db.write(button_name, 'num_block', button.num_block)

    if tem:  # если с шаблоном
        await users_db.write(message.from_user.username, ['n_zamen', 'n_last_shabl'], [u.n_zamen, u.n_last_shabl])

    if button.hidden == 0:  # пишем статистику если кнопка не скрытая
        await stat_db.write(message.text, message.from_user.username)

    if otm:  # если с отметками
        await f_db.write(button.work_file, 'num_line', num_line)
        # лог всегда дб последним действием!
        await log(f'№ строки {message.text}: {num_line}, ({message.from_user.username})\n')
    else:
        await log(f'{message.text}, ({message.from_user.username})\n')


