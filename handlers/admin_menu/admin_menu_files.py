from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.admin_menu_utils import create_menu_back, create_menu_cancel, edit_message, \
    delete_all_after_time, delete_loue_level_menu, create_level_menu

from loader import dp
from filters.admin_filters import CallFilter
from utils.admin_utils import download_sended_file
from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_moderators import moderators_db


class FCM(StatesGroup):
    waite_value_file = State()
    waite_file_name = State()
    waite_delete_file = State()
    waite_file_for_send = State()
    waite_new_file = State()


async def files_keyboard(chat_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if await moderators_db.check_access_moderator(chat_id, 'access_to_files_tools', 'num_line'):
        for file in f_db.files:
            length_file = await f_db.get_len_file(file)
            text = f'{file} --==-- {f_db.files[file].num_line} из {length_file}'
            keyboard.add(InlineKeyboardButton(text=text, callback_data='f_value/' + file))
    if await moderators_db.check_access_moderator(chat_id, 'access_to_files_tools', 'del_file'):
        keyboard.add(InlineKeyboardButton(text='Удалить файл', callback_data='dell_file'))
    if await moderators_db.check_access_moderator(chat_id, 'access_to_files_tools', 'send_me_file'):
        keyboard.add(InlineKeyboardButton(text='Прислать файл с сервера', callback_data='send_file'))
    if await moderators_db.check_access_moderator(chat_id, 'access_to_files_tools', 'add_new_file'):
        keyboard.add(InlineKeyboardButton(text='Загрузить новый файл', callback_data='new_file'))
    if await moderators_db.check_access_moderator(chat_id, 'access_to_files_tools', 'instr'):
        keyboard.add(InlineKeyboardButton(text='Инструкция по загрузке файлов', callback_data='tutor_file'))
    return keyboard


#  ----====  ВЫБОР ФАЙЛА  ====----
@dp.callback_query_handler(text="Настройка файлов", state='*')
async def files_menu(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_options'
    chat_id = call.message.chat.id
    keyboard = await files_keyboard(chat_id)
    text = "Настройка файлов:"

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  ЗАГРУЗИТЬ НОВЫЙ ФАЙЛ ====----
@dp.callback_query_handler(text='new_file', state='*')
async def new_file(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    text = 'В этом режиме можете загрузить любой файл'
    chat_id = call.message.chat.id
    await state.finish()
    await create_menu_cancel(chat_id=chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
    await state.set_state(FCM.waite_new_file.state)
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.message_handler(state=FCM.waite_new_file, content_types=[types.ContentType.DOCUMENT])
async def new_file_2(message: types.Message, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = message.chat.id

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    reply_mess, file_ok = await download_sended_file(message.document.file_id, message.document.file_name)
    if file_ok:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=(reply_mess + 'Новый файл загружен'))
        await edit_message(chat_id=chat_id,
                           type_menu='id_msg_options',
                           keyboard=(await files_keyboard(chat_id)),
                           text=f"Файл '{message.document.file_name}' добавлен")
        await log.write(f'admin_menu: Загружен файл - {message.document.file_name}, ({message.from_user.username})')
    else:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=reply_mess)
    await delete_all_after_time(chat_id)


#  ----====  ИНСТРУКЦИЯ ПО ОТПРАВКЕ ====----
@dp.callback_query_handler(text='tutor_file', state='*')
async def tutor_file(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    files = ", ".join(f_db.files)
    t = "Вы можете отправить боту файлы для работы с ними:\n " \
        "1) При обычной отправке бот заменит старый файл с таким же именем и вернет вам его с " \
        "информацией сколько строк отработано.\n" \
        "(Заменить можно следующие файлы: "f"{files})\n" \
        "2) В меню файлов есть режим 'Загрузить новый файл', после нажатия этой кнопки боту можно отправить файл," \
        " которого раньше небыло.\n" \
        "          ВНИМАНИЕ:\n" \
        "- Если после загрузки файла бот стал неправильно работать, отправьте обратно боту старый файл, " \
        "разберитесь что не так с вашим файлом и снова попробуйте его загрузить.\n" \
        "- Если в файле есть русские символы, убедитесь что его кодировка - UTF8\n" \
        "- Это опасная функция которой можно сломать бота, пользуйтесь осторожно, следите за тем, что вы загружаете."

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=t)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  УДАЛИТЬ ФАЙЛ  ====----
@dp.callback_query_handler(text='dell_file', state='*')
async def dell_file(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    text = "Выберите файл для удаления"
    keyboard = InlineKeyboardMarkup(row_width=1)
    for file in f_db.files:
        if file not in ['name.txt', 'gena.txt']:
            keyboard.add(InlineKeyboardButton(text=f"Удалить {file}", callback_data=f'del_file/{file}'))
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='Отмена'))

    await state.finish()
    await create_menu_cancel(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await state.set_state(FCM.waite_delete_file.state)
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.callback_query_handler(CallFilter(startswith='del_file'), state=FCM.waite_delete_file)
async def dell_file_2(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    file_name = query[1]
    text = f"Файл '{file_name}' Удален из БД, из всех кнопок, его использующих и из папки"

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        if file_name in f_db.files:
            await f_db.write(file_name, 'dell_file')
            await edit_message(chat_id=chat_id,
                               type_menu='id_msg_options',
                               keyboard=(await files_keyboard(chat_id)),
                               text=f"Файл '{file_name}' удален")
            await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
            await log.write(f"admin_menu: файл '{file_name}' удален, ({call.from_user.username})")
        else:
            await create_level_menu(chat_id=chat_id, level=type_menu, text=f"Файл '{file_name}' не найден")
            await log.write(f"admin_menu: Файл '{file_name}' не найден, ({call.from_user.username})")
    except Exception:
        await create_level_menu(chat_id=chat_id, level=type_menu, text=f"Файл '{file_name}' не удалось удалить")
        await log.write(f"admin_menu: файл '{file_name}' не удалось удалить, ({call.from_user.username})")
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


#
#  ----====  ПРИСЛАТЬ ФАЙЛ  ====----
@dp.callback_query_handler(text='send_file', state='*')
async def send_file(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    text = "Выберите файл"
    keyboard = InlineKeyboardMarkup(row_width=1)
    for file in f_db.files:
        keyboard.add(InlineKeyboardButton(text=f"Прислать {file}", callback_data=f'send_file/{file}'))
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='Отмена'))

    await state.finish()
    await create_menu_cancel(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)
    await state.set_state(FCM.waite_file_for_send.state)
    await call.answer()
    await delete_all_after_time(chat_id)


@dp.callback_query_handler(CallFilter(startswith='send_file'), state=FCM.waite_file_for_send)
async def send_file_2(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    file_name = query[1]
    text = f'{file_name} (использовано {f_db.files[file_name].num_line})'

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        if file_name in f_db.files:
            with open('dir_files/' + file_name, 'rb') as f:
                await call.message.answer_document(f, caption=text)
            await log.write(f"admin_menu: файл '{file_name}' выгружен, ({call.from_user.username})")
        else:
            answer = f"Файл '{file_name}' не найден в базе"
            await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
            await log.write(f"admin_menu: {answer}, ({call.from_user.username})")
    except FileNotFoundError:
        answer = f"Файл '{file_name}' не найден"
        await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
        await log.write(f"admin_menu: {answer}, ({call.from_user.username})")
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


#
#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====----
@dp.callback_query_handler(CallFilter(startswith='f_value'), state='*')
async def file_ask_value(call: types.CallbackQuery, state: FSMContext):
    type_menu = 'id_msg_tools'
    chat_id = call.message.chat.id
    query = call.data.split('/')
    file = query[1]
    text = f"Введите № текущей строки для файла '{file}'"

    await state.finish()
    await create_menu_cancel(chat_id)
    await adm_chats_db.write(chat_id=chat_id, tools=['tool'], values=[file])
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    await create_level_menu(chat_id=chat_id, level=type_menu, text=text)
    await state.set_state(FCM.waite_value_file.state)
    await call.answer()
    await delete_all_after_time(chat_id)


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_value_file)
async def file_read_value(message: types.Message, state: FSMContext):

    type_menu = 'id_msg_tools'
    chat_id = message.chat.id
    file = adm_chats_db.chats[message.chat.id].tool
    num = message.text
    len_file = await f_db.get_len_file(file)

    await state.finish()
    await create_menu_back(chat_id)
    await delete_loue_level_menu(chat_id=chat_id, type_menu=type_menu)
    try:
        if num.isdigit() and 0 <= int(num) <= len_file:
            num_line = int(num)
            text = f"№ текущей строки '{num_line}' для файла '{file}' установлено."
            await f_db.write(file, 'n_line', num_line)
            f_db.files[file].num_line = num_line
            await create_level_menu(chat_id=chat_id, level=type_menu, text=text)

            await edit_message(chat_id=chat_id,
                               type_menu='id_msg_options',
                               keyboard=(await files_keyboard(chat_id)),
                               text=f"№ текущей строки '{num_line}' для файла '{file}' установлено")
            await log.write(f"admin_menu: {text} ({message.from_user.username})")
        else:
            answer = f"№ текущей строки '{message.text}' для файла '{file}' не установлено!\n" \
                     f"Введите новое значение.\nЗначение должно быть от 0 до {len_file}"
            await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
            await state.set_state(FCM.waite_value_file.state)
    except Exception:
        answer = f"№ текущей строки '{message.text}' для файла '{file}' не установлено!"
        await create_level_menu(chat_id=chat_id, level=type_menu, text=answer)
        await log.write(f"admin_menu: № текущей строки '{message.text}' для файла '{file}' НЕ установлено!,"
                        f" ({message.from_user.username})\n")
