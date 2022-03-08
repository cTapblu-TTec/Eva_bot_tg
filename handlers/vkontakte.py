from aiogram import types

from loader import dp
from utils.Proverka import prover
from utils.get_text import Vid_Shabl, get_vk_text
from utils.log import log

from work_vs_db.db_users import users_db
from work_vs_db.db_vars import vars_db


# VK_ID
@dp.message_handler(commands=['vk_id'])
async def stor(message: types.Message):
    user = await prover(message, 'vk_otm')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return

    n = message.text[7:].strip()
    k = 9  # сколько выдать отметок

    if n.isdigit() and 1 <= int(n) <= 10:

        for i in range(int(n)):
            text, vars_db.n_vk_id, vars_db.n_get_id = await get_vk_text(vars_db.n_vk_id, vars_db.n_get_id, k, 'vk_id.txt')
            await message.answer(text)
    else:
        text, vars_db.n_vk_id, vars_db.n_get_id = await get_vk_text(vars_db.n_vk_id, vars_db.n_get_id, k, 'vk_id.txt')
        await message.answer(text)

    await vars_db.write(['n_vk_id', 'n_get_id'], [vars_db.n_vk_id, vars_db.n_get_id])
    await log(f'№ vk_id: {vars_db.n_vk_id}, ({message.from_user.username} - /vk_id)\n')


# VK_CLUB
@dp.message_handler(commands=['vk_club'])
async def stor(message: types.Message):
    user = await prover(message, 'vk_otm')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return
    n = message.text[9:].strip()
    k = 10  # сколько выдать отметок

    if n.isdigit() and 1 <= int(n) <= 10:
        for i in range(int(n)):
            text, vars_db.n_vk_club, vars_db.n_get_club = await get_vk_text(vars_db.n_vk_club, vars_db.n_get_club, k, 'vk_club.txt')
            await message.answer(text)
    else:
        text, vars_db.n_vk_club, vars_db.n_get_club = await get_vk_text(vars_db.n_vk_club, vars_db.n_get_club, k, 'vk_club.txt')
        await message.answer(text)

    await vars_db.write(['n_vk_club', 'n_get_club'], [vars_db.n_vk_club, vars_db.n_get_club])
    await log(f'№ vk_club: {vars_db.n_vk_club}, ({message.from_user.username} - /vk_club)\n')


# VK_HTTP
@dp.message_handler(commands=['vk_http'])
async def stor(message: types.Message):
    user = await prover(message, 'vk_otm')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return
    n = message.text[9:].strip()
    k = 10  # сколько выдать отметок

    if n.isdigit() and 1 <= int(n) <= 10:
        for i in range(int(n)):
            text, vars_db.n_vk_http, vars_db.n_get_http = await get_vk_text(vars_db.n_vk_http, vars_db.n_get_http, k, 'vk_http.txt')
            await message.answer(text)
    else:
        text, vars_db.n_vk_http, vars_db.n_get_http = await get_vk_text(vars_db.n_vk_http, vars_db.n_get_http, k, 'vk_http.txt')
        await message.answer(text)

    await vars_db.write(['n_vk_http', 'n_get_http'], [vars_db.n_vk_http, vars_db.n_get_http])
    await log(f'№ vk_http: {vars_db.n_vk_http}, ({message.from_user.username} - /vk_http)\n')


# VK_LOTS
@dp.message_handler(commands=['vk_lots'])
async def stor(message: types.Message):
    user = await prover(message, 'vk_otm')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return
    n = message.text[9:].strip() # сколько выдать блоков
    k = 10  # сколько выдать отметок

    if n.isdigit() and 1 <= int(n) <= 10:
        for i in range(int(n)):
            text, vars_db.n_vk_lots, vars_db.n_get_lots = await get_vk_text(vars_db.n_vk_lots, vars_db.n_get_lots, k, 'vk_lots.txt')
            await message.answer(text)
    else:
        text, vars_db.n_vk_lots, vars_db.n_get_lots = await get_vk_text(vars_db.n_vk_lots, vars_db.n_get_lots, k, 'vk_lots.txt')
        await message.answer(text)

    await vars_db.write(['n_vk_lots', 'n_get_lots'], [vars_db.n_vk_lots, vars_db.n_get_lots])
    await log(f'№ vk_lots: {vars_db.n_vk_lots}, ({message.from_user.username} - /vk_lots)\n')


# VK
@dp.message_handler(commands=['vk'])
async def vk(message: types.Message):
    user = await prover(message, 'vk')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return

    u = users_db.users[message.from_user.username]

    text, vars_db.n_shablon, u.n_zamen, u.n_last_shabl = await Vid_Shabl(vars_db.n_shablon, u.n_zamen,
                                                                         u.n_last_shabl)  # получаем шаблон

    await message.answer(text)

    await users_db.write(message.from_user.username, ['n_zamen', 'n_last_shabl'], [u.n_zamen, u.n_last_shabl])
    await vars_db.write(['n_shablon'], [vars_db.n_shablon])
    await log(f'({message.from_user.username} - /vk)\n')
