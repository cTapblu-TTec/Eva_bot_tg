from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.admin_menu_utils import dellete_old_message, create_menu_back, create_menu_cancel, edit_message, \
    delete_all_after_time

from loader import dp
from filters.callback_filters import ChekFilesForCallback
from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_filess import f_db


class FCM(StatesGroup):
    waite_value_file = State()
    waite_file_name = State()
    waite_delete_file = State()
    waite_file_for_send = State()


async def files_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for file in f_db.files:
        keyboard.add(
            InlineKeyboardButton(text=f'{file} --==-- {f_db.files[file].num_line} из {f_db.files[file].length}',
                                 callback_data=file))
    keyboard.add(InlineKeyboardButton(text='Добавить файл', callback_data='add_file'))
    keyboard.add(InlineKeyboardButton(text='Удалить файл', callback_data='dell_file'))
    keyboard.add(InlineKeyboardButton(text='Прислать файл с сервера', callback_data='send_file'))
    keyboard.add(InlineKeyboardButton(text='Инструкция по загрузке файлов', callback_data='tutor_file'))
    return keyboard


#  ----====  ВЫБОР ФАЙЛА  ====----
@dp.callback_query_handler(text="Настройка файлов", state='*')
async def settings_files(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_options')
    # id_msg_options
    keyboard = await files_keyboard()
    msg = await call.message.answer("Настройка файлов:", reply_markup=keyboard)

    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_options'], values=[msg["message_id"]])
    await call.answer()
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    await delete_all_after_time(call.message.chat.id)


#  ----====  ИНСТРУКЦИЯ ПО ОТПРАВКЕ ====----
@dp.callback_query_handler(text='tutor_file', state='*')
async def add_button(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    send = call.message.answer
    files = ".txt, ".join(f_db.files_names)
    await send("- Вы можете отправить боту новые файлы для работы с ними. Бот вернет вам взамен новых старые с "
               "информацией сколько строк отработано.\n- Заменить можно следующие файлы: "f"{files}.txt\n"
               "- Если после замены файла бот стал неправильно работать, отправьте обратно боту старый файл, "
               "разберитесь что не так с вашим файлом и снова попробуйте его загрузить.\n"
               "- Если в файле есть русские символы, убедитесь что его кодировка - UTF8\n"
               "- Это опасная функция которой можно сломать бота, пользуйтесь осторожно, следите за тем, что вы "
               "загружаете.")
    await call.answer()


#  ----====  ДОБАВИТЬ ФАЙЛ  ====----
@dp.callback_query_handler(text='add_file', state='*')
async def add_button(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    await call.message.answer("Введите имя файла")
    await state.set_state(FCM.waite_file_name.state)
    await call.answer()


@dp.message_handler(state=FCM.waite_file_name)
async def add_button(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    file_name = message.text
    # todo проверка корректности имени файла
    try:
        if file_name not in f_db.files:
            await f_db.write(file_name, 'add_file', '')
            await edit_message(chat_id=message.chat.id,
                               type_menu='id_msg_options',
                               keyboard=(await files_keyboard()),
                               text=f"Файл '{file_name}' добавлен")
            await message.answer(f"Файл '{file_name}' добавлен")
            await log.write(f"admin: файл '{file_name}' добавлен, ({message.from_user.username})\n")
        else:
            await message.answer(f"Файл '{file_name}' уже есть")
            await log.write(f"admin: файл '{file_name}' уже есть, ({message.from_user.username})\n")
    except Exception:
        await message.answer(f"Файл '{file_name}' не удалось добавить")
        await log.write(f"admin: файл '{file_name}' не удалось добавить, ({message.from_user.username})\n")


#  ----====  УДАЛИТЬ ФАЙЛ  ====----
@dp.callback_query_handler(text='dell_file', state='*')
async def dell_button(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')

    keyboard = InlineKeyboardMarkup(row_width=1)
    for file in f_db.files:
        keyboard.add(InlineKeyboardButton(text=f"Удалить {file}", callback_data=file))
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='Отмена'))
    msg = await call.message.answer("Выберите файл для удаления", reply_markup=keyboard)

    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_tools'], values=[msg["message_id"]])
    await state.set_state(FCM.waite_delete_file.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


# Если вместо кнопки удаления пользователь что-то ввел
@dp.message_handler(state=FCM.waite_delete_file)
async def settings_button_tool(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    await dellete_old_message(chat_id=message.chat.id, type_menu='id_msg_tools')


@dp.callback_query_handler(state=FCM.waite_delete_file)
async def dell_button(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    if call.data == 'Отмена':
        return

    file_name = call.data
    delete = False
    try:
        if file_name in f_db.files:
            await f_db.write(file_name, 'dell_file', '')
            await edit_message(chat_id=call.message.chat.id,
                               type_menu='id_msg_options',
                               keyboard=(await files_keyboard()),
                               text=f"Файл '{file_name}' удален")
            await call.message.answer(f"Файл '{file_name}' Удален")
            delete = True
        else:
            await call.message.answer(f"Файл '{file_name}' не найден")
    except Exception:
        await call.message.answer(f"Файл '{file_name}' не удалось удалить")
    await call.answer()
    if delete:
        await log.write(f"admin: файл '{file_name}' удален, ({call.message.chat.username})\n")
    else:
        await log.write(f"admin: файл '{file_name}' не удален, ({call.message.chat.username})\n")
    await delete_all_after_time(call.message.chat.id)


#
#  ----====  ПРИСЛАТЬ ФАЙЛ  ====----
@dp.callback_query_handler(text='send_file', state='*')
async def send_file(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')

    keyboard = InlineKeyboardMarkup(row_width=1)
    for file in f_db.files:
        keyboard.add(InlineKeyboardButton(text=f"Прислать {file}", callback_data=file))
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='Отмена'))
    msg = await call.message.answer("Выберите файл", reply_markup=keyboard)

    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_tools'], values=[msg["message_id"]])
    await state.set_state(FCM.waite_file_for_send.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


# Если вместо кнопки удаления пользователь что-то ввел
@dp.message_handler(state=FCM.waite_file_for_send)
async def send_file_2_1(message: types.Message, state: FSMContext):
    await state.finish()
    await create_menu_back(message.chat.id)
    await dellete_old_message(chat_id=message.chat.id, type_menu='id_msg_tools')


@dp.callback_query_handler(state=FCM.waite_file_for_send)
async def send_file_2(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    if call.data == 'Отмена':
        return

    file_name = call.data
    try:
        if file_name in f_db.files:
            with open('dir_files/' + file_name, 'rb') as f:
                await call.message.answer_document(f, caption=f'{file_name} (использовано '
                                                              f'{f_db.files[file_name].num_line})')
            await log.write(f"admin: файл '{file_name}' отправлен, ({call.message.chat.username})\n")
        else:
            await call.message.answer(f"Файл '{file_name}' не найден в базе")
            await log.write(f"admin: файл '{file_name}' не найден в базе, ({call.message.chat.username})\n")
    except FileNotFoundError:
        await call.message.answer(f"Файл '{file_name}' не найден")
        await log.write(f"admin: файл '{file_name}' не найден, ({call.message.chat.username})\n")
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


#
#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====----
@dp.callback_query_handler(ChekFilesForCallback(), state='*')
async def settings_button_tool(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)

    file = call.data
    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['tool'], values=[file])

    await call.message.answer(f"Введите № текущей строки для файла '{file}'")
    await state.set_state(FCM.waite_value_file.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_value_file)
async def settings_button_tool(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Отмена':
        await create_menu_back(message.chat.id)
        return
    file = adm_chats_db.chats[message.chat.id].tool

    try:
        num_line = int(message.text)
        # todo проверка с длиной файла
        await f_db.write(file, 'n_line', num_line)
        f_db.files[file].num_line = num_line

        await create_menu_back(chat_id=message.chat.id,
                               text=f"№ текущей строки '{num_line}' для файла '{file}' установлено.")

        await edit_message(chat_id=message.chat.id,
                           type_menu='id_msg_options',
                           keyboard=(await files_keyboard()),
                           text=f"№ текущей строки '{num_line}' для файла '{file}' установлено")

        await log.write(f"admin: № текущей строки '{num_line}' для файла '{file}' установлено,"
                        f" ({message.from_user.username})\n")

    except Exception:
        await message.answer(f"№ текущей строки '{message.text}' для файла '{file}' не установлено!\n"
                             f"Введите новое значение")
        await state.set_state(FCM.waite_value_file.state)

        await log.write(f"admin: № текущей строки '{message.text}' для файла '{file}' НЕ установлено!,"
                        f" ({message.from_user.username})\n")
