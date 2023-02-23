from asyncio import create_task

from aiogram import types
from filters.users_filters import FilterForGeneral
from loader import dp, bot
from utils.gena import gennadij
from utils.get_text import get_link_list, get_template
from utils.log import log
from utils.notify_admins import notify
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


async def work_buttons(button_name, button, username, bot, chat):

    number = ''
    template = ''
    links = ''

    # НОМЕР БЛОКА
    if button.num_block:
        if button.name_block:
            number = f'{button.num_block} {button.name_block}\n'
        else:
            number = f'{button.num_block}\n'
        buttons_db.buttons[button_name].num_block += 1
    elif button.name_block:
        number = f'{button.name_block}\n'

    # ШАБЛОН
    if button.shablon_file and button.shablon_file != 'gena.txt':
        u = users_db.users[username]
        template, u.n_zamen, u.n_last_shabl = await get_template(u.n_zamen, u.n_last_shabl, button.shablon_file)
        users_db.users[username].n_zamen = u.n_zamen
        users_db.users[username].n_last_shabl = u.n_last_shabl
    # ГЕНА
    elif button.shablon_file == 'gena.txt':
        template = await gennadij.get_text()

    # ОТМЕТКИ
    if button.work_file:
        try:
            num_line = f_db.files[button.work_file].num_line
            file = f_db.files[button.work_file].name
            links, num_line = await get_link_list(num_line, button.size_blok, file, button_name)
            f_db.files[button.work_file].num_line = num_line
        except Exception:
            await notify(f'Файл {button.work_file} отсутствует в базе в таблице filess')

    # КЛАВИАТУРА
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Назад', button_name])

    # ВЫДАЧА БЛОКА
    text = number + template + links
    if text:
        if button.num_block:
            await bot.send_message(chat, text, reply_markup=keyboard)
        else:
            create_task(bot.send_message(chat, text, reply_markup=keyboard))


@dp.message_handler(FilterForGeneral())
async def general_hendler(message: types.Message):
    button_name = message.text
    button = buttons_db.buttons[button_name]
    username = message.from_user.username
    users_db.users[username].last_button = button_name
    blocks = users_db.users[username].blocks
    chat_id = message.chat.id

    for i in range(blocks):
        await work_buttons(button_name, button, username, bot, chat_id)

    # ЗАПИСЬ В БД
    # пишем статистику если кнопка не скрытая и в статистике
    if button.hidden == 0 and button.statistical == 1:
        await stat_db.write(button_name, username, blocks)

    # если с номером
    if button.num_block:
        await buttons_db.write(button_name, 'n_block', buttons_db.buttons[button_name].num_block)

    # если с шаблоном
    if button.shablon_file and button.shablon_file != 'gena.txt':
        await users_db.write(username, ['n_zamen', 'n_last_shabl', 'last_button'],
                             [users_db.users[username].n_zamen, users_db.users[username].n_last_shabl, button_name])

    # клавиатура
    else:
        await users_db.write(username, ['last_button'], [button_name])

    # если с отметками
    if button.work_file:
        await f_db.write(button.work_file, 'n_line', f_db.files[button.work_file].num_line)
        await log.write(f'{button_name} Х{blocks}, № строки {f_db.files[button.work_file].num_line}, ({username})')
    else:
        await log.write(f'{button_name} Х{blocks}, ({username})')
