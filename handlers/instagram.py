from aiogram import types

from loader import dp
from utils.Proverka import prover
from utils.get_text import Vid_Shabl, Vid_Otmetok, s
from utils.log import log
from utils.gena import gennadij

from work_vs_db.db_users import users_db
from work_vs_db.db_vars import vars_db


@dp.message_handler(commands=['gena'])
async def gena(message: types.Message):
    user = await prover(message, 'other')  # проверяем статус пользователя и пишем статистику
    if user != "admin": return

    text = await gennadij.get_text()
    await message.answer(text)


# n_zamen - счетчик замены слов, n_storis - счетчик сторис
# n_last_shabl - номера последних шаблонов, выданных пользователю
# SHABLON
@dp.message_handler(commands=['shablon'])
async def shab(message: types.Message):
    user = await prover(message, 'shablon')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return

    # ВНИМАНИЕ - здесть нужно заменить на get_user с проверкой наличия Админа в списке!!
    u = users_db.users[message.from_user.username]

    k = 3  # сколько выдать отметок

    text, vars_db.n_shablon, u.n_zamen, u.n_last_shabl = \
        await Vid_Shabl(vars_db.n_shablon, u.n_zamen, u.n_last_shabl)  # получаем шаблон
    text, vars_db.n_otmetki, u.n_last_otm, s.l_otm_vernuli = \
        await Vid_Otmetok(text, vars_db.n_otmetki, k, s.l_otm_vernuli)  # получаем отметки

    await message.answer(text)

    await users_db.write(message.from_user.username, ['n_last_otm', 'n_zamen', 'n_last_shabl'],
                         [u.n_last_otm, u.n_zamen, u.n_last_shabl])
    await vars_db.write(['n_otmetki', 'n_shablon'], [vars_db.n_otmetki, vars_db.n_shablon])
    await log(f'№ отметки: {vars_db.n_otmetki} ({message.from_user.username} - /shablon)\n')


# STORIS
@dp.message_handler(commands=['storis'])
async def stor(message: types.Message):
    user = await prover(message, 'storis')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return

    u = users_db.users[message.from_user.username]

    k = 9  # сколько выдать отметок

    text, vars_db.n_otmetki, u.n_last_otm, s.l_otm_vernuli = await Vid_Otmetok('', vars_db.n_otmetki, k,
                                                                               s.l_otm_vernuli)  # получаем отметки
    text = str(vars_db.n_storis) + '\n' + text  # присваиваем номер

    await message.answer(text)

    await users_db.write(message.from_user.username, ['n_last_otm'], [u.n_last_otm])
    await vars_db.write(['n_otmetki', 'n_storis'], [vars_db.n_otmetki, vars_db.n_storis + 1])
    await log(
        f'№ отметки: {vars_db.n_otmetki}, № сторис: {vars_db.n_storis} ({message.from_user.username} - /storis)\n')


# OTMETKI
@dp.message_handler(commands=['otmetki'])
async def otm(message: types.Message):
    user = await prover(message, 'otmetki')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return

    u = users_db.users[message.from_user.username]

    k = 5  # сколько выдать отметок

    text, vars_db.n_otmetki, u.n_last_otm, s.l_otm_vernuli = await Vid_Otmetok('', vars_db.n_otmetki, k,
                                                                               s.l_otm_vernuli)  # получаем отметки

    await message.answer(text)

    await users_db.write(message.from_user.username, ['n_last_otm'], [u.n_last_otm])
    await vars_db.write(['n_otmetki'], [vars_db.n_otmetki])
    await log(f'№ отметки: {vars_db.n_otmetki}, ({message.from_user.username} - /otmetki)\n')


# VERNUT
@dp.message_handler(commands=['vern'])
async def vernut(message: types.Message):
    user = await prover(message, 'other')  # проверяем статус пользователя и пишем статистику
    if user == "guest": return

    u = users_db.users[message.from_user.username]

    if u.n_last_otm is None or u.n_last_otm == 0:
        await message.answer("Вы не брали отметок")
        return

    else:
        list_o = []
        for i in u.n_last_otm:
            x = i.find('@')
            y = i.find('\\')
            if y != -1:
                list_o.append(i[x:y])
            else:
                list_o.append(i[x:])

        s.l_otm_vernuli += list_o  # добавляем возвращенные отметки в список
        await message.answer("отметки, " + str(len(list_o)) + "шт. возвращены боту")
    await users_db.write(message.from_user.username, ['n_last_otm'], [0])
    await log('Вернула отметки ({message.from_user.username} - /vern)\n')
