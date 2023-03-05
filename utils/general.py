from asyncio import create_task

from aiogram import types
from loader import bot
from utils.gena import gennadij
from utils.get_text import get_link_list, get_template
from utils.log import log
from utils.notify_admins import notify_admins
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


async def get_block(button_name, button, username):
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
            await notify_admins(f'Файл {button.work_file} отсутствует в базе в таблице filess')

    # ВЫДАЧА БЛОКА
    text = number + template + links
    return text


async def general(text, username, chat_id, blocks=1):
    num_x = text.rfind('Х')
    blocks_str = text[num_x + 1:]
    if blocks_str.isdigit() and 1 <= int(blocks_str) <= 10:
        button_name = text[:num_x - 1]
        blocks = int(blocks_str)
    else:
        button_name = text
    button = buttons_db.buttons[button_name]
    users_db.users[username].last_button = button_name

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Назад', button_name + ' Х' + str(blocks)])

    for i in range(blocks):
        text = await get_block(button_name, button, username)
        if text:
            if blocks > 1 and button.num_block:
                await bot.send_message(chat_id, text, reply_markup=keyboard)
            else:
                create_task(bot.send_message(chat_id, text, reply_markup=keyboard))
        else:
            await bot.send_message(chat_id, 'Пустой блок')
            await notify_admins(f'{button_name} - Пустой блок, настройте кнопку ({username})')
            await log.write(f'{button_name} - Пустой блок, настройте кнопку ({username})', user='admin')
            return

    # ЗАПИСЬ В БД
    # пишем статистику если кнопка не скрытая и в статистике
    await stat_db.write(button_name, username, blocks)

    # если с номером
    if button.num_block:
        await buttons_db.write(button_name, 'n_block', buttons_db.buttons[button_name].num_block)

    # если с шаблоном
    if button.shablon_file and button.shablon_file != 'gena.txt':
        await users_db.write(
            username,
            ['n_zamen', 'n_last_shabl', 'last_button'],
            [users_db.users[username].n_zamen, users_db.users[username].n_last_shabl, button_name])

    # клавиатура
    else:
        await users_db.write(username, ['last_button'], [button_name])

    # если с отметками
    if button.work_file:
        num_line = f_db.files[button.work_file].num_line
        await f_db.write(button.work_file, 'n_line', num_line)
        await log.write(text=f'{button_name} Х{blocks} - {num_line}', user=username)
    else:
        await log.write(f'{button_name} Х{blocks}', user=username)
