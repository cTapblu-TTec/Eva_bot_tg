from aiogram import types
import sys
from aiogram.utils.exceptions import BadRequest

from data.config import ADMIN_LOG_CHAT
from filters.admin_filters import FilterCheckAdmin
from loader import dp
from utils.log import log
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_users import users_db


@dp.message_handler(FilterCheckAdmin(), commands=['admin'])
async def adm_commands(message: types.Message):
    await message.answer(
         "/set - тонкая настройка файлов\n"
         "/set_b - тонкая настройка кнопок\n"
         "/read_bd - чтение БД после корректировки\n"
         "/adUser - добавить пользователя\n"
         "/dlUser - удалить пользователя\n"
         "/exit - выключить бота\n"
         "/sys - память системы\n"
         "/send_log - прислать файл лога\n"
         "/clear_log - очистить файл лога"
    )
    await log.write(f'admin: {message.text}, ({message.from_user.username})')


@dp.message_handler(FilterCheckAdmin(), commands=['set'])
async def adm_set_files(message: types.Message):
    text = message.text[5:].strip()
    ass = False
    if text != '':
        zapros = text.split(' ')
        if zapros[0] in f_db.files:
            if zapros[1] in ('num_line', 'active'):
                if zapros[2]:
                    await f_db.write(zapros[0], [zapros[1]], [zapros[2]])
                    await message.answer("Значение установлено, для проверки нажмите /st")
                    await log.write(f'admin: {message.text}, ({message.from_user.username})')
                else:
                    ass = True
            else:
                ass = True
        else:
            ass = True
    else:
        ass = True
    if ass:
        await message.answer("Ошибка ввода, пример:\n/set vk_gruppa.txt num_line 0\n"
                             f"список доступных файлов:\n{list(f_db.files)}\n"
                             "список доступных переменных:\n"
                             "'num_line', 'active'(0,1)")


@dp.message_handler(FilterCheckAdmin(), commands=['set_b'])
async def adm_set_butt(message: types.Message):
    text = message.text[7:].strip()
    ass = False
    if text != '':
        zapros = text.split(' ')
        if zapros[0] in buttons_db.buttons:
            if zapros[1] in ('group_buttons', 'work_file', 'num_block', 'size_blok', 'shablon_file', 'active'):
                if zapros[2]:
                    await buttons_db.write(zapros[0], [zapros[1]], [zapros[2]])
                    await message.answer("Значение установлено")
                    await log.write(f'admin: {message.text}, ({message.from_user.username})')
                else:
                    ass = True
            else:
                ass = True
        else:
            ass = True
    else:
        ass = True
    if ass:
        await message.answer("Ошибка ввода, пример:\nset_b work_file vk_gruppa.txt\n"
                             f"список доступных кнопок:\n{', '.join(buttons_db.buttons)}\n"
                             "список доступных переменных:\n"
                             "'group_buttons', 'work_file', 'num_block', "
                             "'size_blok'(1-10), 'shablon_file', 'active'(0,1)")


@dp.message_handler(FilterCheckAdmin(), commands=['read_bd'])
async def adm_read_bd(message: types.Message):
    await f_db.create(None)
    await buttons_db.create()
    await groups_db.create(None)

    await message.answer("Данные обновлены из базы данных")
    await log.write(f'admin: {message.text}, ({message.from_user.username})')


@dp.message_handler(FilterCheckAdmin(), commands=['exit'])
async def adm_exit(message: types.Message):
    await log.send_log_now()
    await dp.bot.send_message(ADMIN_LOG_CHAT, f"БОТ ОСТАНОВЛЕН!, ({message.from_user.username})")
    sys.exit()


@dp.message_handler(FilterCheckAdmin(), commands=['sys'])
async def adm_exit(message: types.Message):
    import psutil
    text = ''
    part = psutil.disk_partitions()
    for disk in part:
        try:
            hd = psutil.disk_usage(disk.device)
            hd_total = hd.total / (1024 * 1024 * 1024)
            hd_used = hd.used / (1024 * 1024 * 1024)
            text += f"used {hd_used:.4} from {hd_total:.4} Gb disk {disk.device} ({hd.percent}%)\n"
        except Exception:
            pass

    mem = psutil.virtual_memory()
    mem_total = mem.total / (1024 * 1024 * 1024)
    mem_used = mem.used / (1024 * 1024 * 1024)

    await message.answer(text +
                         f"used {mem_used:.4} from {mem_total:.4} Gb memory ({mem.percent}%)")


@dp.message_handler(FilterCheckAdmin(), commands=['adUser'])
async def adm_ad_user(message: types.Message):
    new_user = message.text[8:]
    answer = await users_db.add_user(new_user)
    await message.answer(answer)
    await log.write(f'admin: {answer}, ({message.from_user.username})')


@dp.message_handler(FilterCheckAdmin(), commands=['dlUser'])
async def adm_dell_user(message: types.Message):
    user = message.text[8:]
    answer = await users_db.del_user(user)
    await message.answer(answer)
    await log.write(f'admin: {answer}, ({message.from_user.username})')


@dp.message_handler(FilterCheckAdmin(), commands=['send_log'])
async def adm_dell_user(message: types.Message):
    mess = 'Системный лог'
    try:
        with open('log.log', 'rb') as f:
            await message.reply_document(f, caption=mess)
    except (FileNotFoundError, BadRequest):
        mess = 'Лог не найден'
        await message.answer(mess)
    finally:
        await log.write(f'admin: {mess}, ({message.from_user.username})')


@dp.message_handler(FilterCheckAdmin(), commands=['clear_log'])
async def adm_dell_user(message: types.Message):
    mess = 'Лог очищен'
    try:
        with open('log.log', 'w'):
            pass
    except FileNotFoundError:
        mess = 'Файл не найден'
    finally:
        await message.answer(mess)
        await log.write(f'admin: {mess}, ({message.from_user.username})')
