from aiogram import types

import utils.get_text
from data.config import ADMINS
from loader import dp
from work_vs_db.db_statistic import stat_db
from work_vs_db.db_users import users_db
from work_vs_db.db_vars import vars_db


@dp.message_handler(commands=['admin'])
async def ad_m(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await message.answer("/st - количество отметок и шаблонов\n"
                             "/stUsers - статистика пользователей\n"
                             "/setOtm ХХ - установка позиции отметок\n"
                             "/setStor ХХ - установка счетчика сторис\n"
                             "/reStUr - сброс статистики пользователей\n"
                             "/adUser ник - добавить пользователя\n"
                             "/dlUser ник - удалить пользователя\n"
                             "/users - вывести список пользователей\n"
                             "/set_vk_id - установка ВК сторис\n"
                             "/set_vk_http - установка ВК людей\n"
                             "/set_vk_club - установка ВК групп\n"
                             "/set_vk_lots - установка ВК лотерей\n"
                             "/files - инструкция по отправки файла")
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.answer("Вы не админ этого бота, извините")


@dp.message_handler(commands=['users'])
async def dlu(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        users_names = users_db.users_names
        users_names.sort(key=str.lower)
        await message.answer("\n".join(users_names))
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.answer("Вы не админ этого бота, извините")


@dp.message_handler(commands=['st'])
async def st(message: types.Message):
    if str(message.from_user.id) in ADMINS or message.from_user.username == 'dariasuv':
        lo = len(utils.get_text.s.l_otmetki)
        ls = len(utils.get_text.s.l_polina)
        text_vk = ''
        fails = ['vk_club.txt', 'vk_http.txt', 'vk_id.txt', 'vk_lots.txt']
        vars_ = [vars_db.n_vk_club, vars_db.n_vk_http, vars_db.n_vk_id, vars_db.n_vk_lots]
        k = 0
        for i in fails:
            with open(i, "r") as f:
                len_ = len(f.readlines())
            text_vk += f'{i} использовано {vars_[k]} из {len_}\n'
            k += 1

        await message.answer(f"otmetki.txt использовано {vars_db.n_otmetki} из {lo}\n"
                             f"Шаблонов использовано {vars_db.n_shablon} из  {ls}\n"
                             + text_vk)
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.answer("Вы не админ этого бота, извините")


@dp.message_handler(commands=['stUsers'])
async def stu(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await stat_db.get_html()
        file = open('statistic.html', 'rb')
        # await dp.bot.send_document(int(admin), file)
        await message.reply_document(file)
        file.close()

    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.answer("Вы не админ этого бота, извините")


@dp.message_handler(commands=['setOtm'])
async def ad_so(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        num = message.text[8:].strip()
        if num.isdigit():  # если число
            await vars_db.write(['n_otmetki'], [int(num)])
            await message.answer("Отметки установлены, для проверки нажмите /st")
        else:
            await message.answer("Ошибка ввода, пример команды: /setOtm 100")
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.answer("Вы не админ этого бота, извините")


@dp.message_handler(commands=['setStor'])
async def ad_rs(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        num = message.text[9:].strip()
        if num.isdigit() and 1 <= int(num) <= 500:
            await vars_db.write(['n_storis'], [int(num)])
            await message.answer("Следующий сторис будет с номером " + num)
        else:
            await message.answer("Ошибка ввода, пример команды: /reStor 1")
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.answer("Вы не админ этого бота, извините")


@dp.message_handler(commands=['reStUr'])
async def ad_rs(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await stat_db.clear()
        await vars_db.write(['n_shablon'], [0])
        await message.answer("Cтатистика по пользователям и счетчик шаблонов сброшены. /stUsers")
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.answer("Вы не админ этого бота, извините")


@dp.message_handler(commands=['set_vk_id'])
async def ad_rs(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        num = message.text[11:].strip()
        if num.isdigit() and 0 <= int(num) <= 30000:
            await vars_db.write(['n_vk_id', 'n_get_id'], [int(num), 1])
            await message.answer(f'позиция ВК сторисов установлена на {num}\n'
                                 'счетчик ВК сторисов начнётся с 1')
        else:
            await message.answer("ошибка ввода, пример комманды: /set_vk_id 100")
    else:
        await message.answer("Вы не админ этого бота, извините")
        await stat_db.write('other', message.from_user.username)  # пишем статистику


@dp.message_handler(commands=['set_vk_club'])
async def ad_rs(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        num = message.text[13:].strip()
        if num.isdigit() and 0 <= int(num) <= 30000:
            await vars_db.write(['n_vk_club', 'n_get_club'], [int(num), 1])
            await message.answer(f'позиция ВК групп установлена на {num}\n'
                                 'счетчик ВК групп начнётся с 1')
        else:
            await message.answer("ошибка ввода, пример комманды: /set_vk_club 100")
    else:
        await message.answer("Вы не админ этого бота, извините")
        await stat_db.write('other', message.from_user.username)  # пишем статистику


@dp.message_handler(commands=['set_vk_http'])
async def ad_rs(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        num = message.text[13:].strip()
        if num.isdigit() and 0 <= int(num) <= 30000:
            await vars_db.write(['n_vk_http', 'n_get_http'], [int(num), 1])
            await message.answer(f'позиция ВК людей установлена на {num}\n'
                                 'счетчик ВК людей начнётся с 1')
        else:
            await message.answer("ошибка ввода, пример комманды: /set_vk_http 100")
    else:
        await message.answer("Вы не админ этого бота, извините")
        await stat_db.write('other', message.from_user.username)  # пишем статистику


@dp.message_handler(commands=['set_vk_lots'])
async def ad_rs(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        num = message.text[13:].strip()
        if num.isdigit() and 0 <= int(num) <= 30000:
            await vars_db.write(['n_vk_lots', 'n_get_lots'], [int(num), 1])
            await message.answer(f'позиция ВК лотерей установлена на {num}\n'
                                 'счетчик ВК лотерей начнётся с 1')
        else:
            await message.answer("ошибка ввода, пример комманды: /set_vk_lots 100")
    else:
        await message.answer("Вы не админ этого бота, извините")
        await stat_db.write('other', message.from_user.username)  # пишем статистику


@dp.message_handler(commands=['files'])
async def ad_m(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await message.answer("- Вы можете отправить боту новые файлы для работы с ними. "
                             "Бот вернет вам взамен новых старые с информацией сколько строк отработано.\n"
                             "- Заменить можно следующие файлы: otmetki.txt, vk_id.txt, vk_club.txt, vk_lots.txt,"
                             " vk_http.txt, polina.txt, name.txt\n"
                             "- Если после замены файла бот стал неправильно работать, отправьте обратно боту старый "
                             "файл, разберитесь что не так с вашим файлом и снова попробуйте его загрузить.\n"
                             "- После успешной загрузки и проверки работы бота не забудьте сбросить соответствующую "
                             "файлу переменную (команды set).\n"
                             "- Если в файле есть русские символы, убедитесь что его кодировка - UTF8\n"
                             "- Это опасная функция которой можно сломать бота, пользуйтесь осторожно, следите за тем,"
                             " что вы загружаете.")
    else:
        await stat_db.write('other', message.from_user.username)  # пишем статистику
        await message.answer("Вы не админ этого бота, извините")
