from aiogram import types

from loader import dp
from utils.face_control import control
from utils.log import log
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


@dp.message_handler(commands=['admin'])
async def adm_commands(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    await message.answer("/st - количество отметок и шаблонов\n"    
                         "/stUsers - статистика пользователей\n"
                         "/reStUr - сброс статистики пользователей\n"
                         "/adUser ник - добавить пользователя\n"
                         "/dlUser ник - удалить пользователя\n"
                         "/users - вывести список пользователей\n"
                         "/buttons - список кнопок и файлов\n"
                         "/set - тонкая настройка файлов\n"
                         "/set_b - тонкая настройка кнопок\n"
                         "/read_bd - чтение БД после корректировки\n"
                         "/files - инструкция по отправке файла")
    await log(f'admin: {message.text}, ({message.from_user.username})\n')


@dp.message_handler(commands=['buttons'])
async def adm_users(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    text = 'имя - отметки - шаблоны\n\n'
    for button in buttons_db.buttons:
        text += f"{buttons_db.buttons[button].name} - {buttons_db.buttons[button].work_file}" \
                f" - {buttons_db.buttons[button].shablon_file}\n"

    await message.answer(text)
    await log(f'admin: {message.text}, ({message.from_user.username})\n')


@dp.message_handler(commands=['users'])
async def adm_users(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    users_names = users_db.users_names
    num = len(users_names)
    users_names.sort(key=str.lower)
    users = "\n".join(users_names)
    await message.answer(f'Всего {num} пользователей:\n{users}')
    await log(f'admin: {message.text}, ({message.from_user.username})\n')


@dp.message_handler(commands=['st'])
async def adm_stat(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin" and message.from_user.username != 'dariasuv':
        await message.answer("Вы не админ этого бота, извините")
        return

    stat = ''
    for file in f_db.files:
        try:
            with open('dir_files/'+file, "r") as f:
                len_ = len(f.readlines())
            stat += f'{f_db.files[file].name} -- {f_db.files[file].num_line} из {len_}\n'
        except Exception:
            await message.answer(f'файл {file} не найден')
    await message.answer(stat)
    await log(f'admin: {message.text}, ({message.from_user.username})\n')


@dp.message_handler(commands=['stUsers'])
async def adm_stat_users(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    await stat_db.get_html()
    with open('statistic.html', 'rb') as file:
        await message.reply_document(file)
    await log(f'admin: {message.text}, ({message.from_user.username})\n')


@dp.message_handler(commands=['reStUr'])
async def adm_reset_stat_users(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    await stat_db.dell()
    await stat_db.create(None)
    await message.answer("Cтатистика по пользователям сброшена. /stUsers")
    await log(f'admin: {message.text}, ({message.from_user.username})\n')


@dp.message_handler(commands=['files'])
async def adm_files(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return
    files = ".txt, ".join(f_db.files_names)
    await message.answer("- Вы можете отправить боту новые файлы для работы с ними. "
                         "Бот вернет вам взамен новых старые с информацией сколько строк отработано.\n"
                         "- Заменить можно следующие файлы: "
                         f"{files}.txt\n"
                         "- Если после замены файла бот стал неправильно работать, отправьте обратно боту старый "
                         "файл, разберитесь что не так с вашим файлом и снова попробуйте его загрузить.\n"
                         "- После успешной загрузки и проверки работы бота не забудьте сбросить соответствующую "
                         "файлу переменную (команды set).\n"
                         "- Если в файле есть русские символы, убедитесь что его кодировка - UTF8\n"
                         "- Это опасная функция которой можно сломать бота, пользуйтесь осторожно, следите за тем,"
                         " что вы загружаете.")
    await log(f'admin: {message.text}, ({message.from_user.username})\n')


@dp.message_handler(commands=['set'])
async def adm_set_files(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    text = message.text[5:].strip()
    ass = False
    if text != '':
        zapros = text.split(' ')
        if zapros[0][:-4] in f_db.files_names:
            if zapros[1] in ('num_line', 'num_block', 'size_blok', 'active'):
                if zapros[2].isdigit:
                    await f_db.write(zapros[0], [zapros[1]], [int(zapros[2])])
                    await message.answer("Значение установлено, для проверки нажмите /st")
                    await log(f'admin: {message.text}, ({message.from_user.username})\n')
                else: ass = True
            else: ass = True
        else: ass = True
    else: ass = True
    if ass: await message.answer("Ошибка ввода, пример:\n/set vk_gruppa.txt num_line 0\n"
                                 f"список доступных файлов:\n{f_db.files_names}\n"
                                 "список доступных переменных:\n"
                                 "'num_line', 'active'(0,1)")


@dp.message_handler(commands=['set_b'])
async def adm_set_butt(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    text = message.text[7:].strip()
    ass = False
    if text != '':
        zapros = text.split(' ')
        if zapros[0] in buttons_db.buttons_names:
            if zapros[1] in ('group_buttons', 'work_file', 'num_block', 'size_blok', 'shablon_file', 'active'):
                if zapros[2]:
                    if zapros[2].isdigit: zapros[2] = int(zapros[2])
                    await buttons_db.write(zapros[0], [zapros[1]], [zapros[2]])
                    await message.answer("Значение установлено")
                    await log(f'admin: {message.text}, ({message.from_user.username})\n')
                else: ass = True
            else: ass = True
        else: ass = True
    else: ass = True
    if ass: await message.answer("Ошибка ввода, пример:\nset_b work_file vk_gruppa.txt\n"
                                 f"список доступных кнопок:\n{buttons_db.buttons_names}\n"
                                 "список доступных переменных:\n"
                                 "'group_buttons', 'work_file', 'num_block', "
                                 "'size_blok'(1-10), 'shablon_file', 'active'(0,1)")


@dp.message_handler(commands=['read_bd'])
async def adm_read_bd(message: types.Message):
    user = await control(message)  # проверяем статус пользователя
    if user != "admin":
        await message.answer("Вы не админ этого бота, извините")
        return

    await f_db.create(None)
    await buttons_db.create(None)
    await groups_db.create(None)

    await message.answer("Данные обновлены из базы данных")
    await log(f'admin: {message.text}, ({message.from_user.username})\n')

    # dp.register_message_handler(work_buttons, text=buttons_db.buttons_names)
