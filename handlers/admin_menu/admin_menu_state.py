from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp
from utils.admin_utils import get_button_clicks
from utils.face_control import Guests
from utils.log import log
from utils.user_utils import create_user_menu
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_moderators import moderators_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


@dp.message_handler(text='Мониторинг', state='*')
async def start_menu(message: types.Message, state: FSMContext):
    async def start_menu_keyboard():
        settings_buttons = {
            'Кнопки - группы - № блоков': 'buttons_groups', 'Кнопки - файлы - нажатия': 'buttons_files',
            'Список файлов': 'list_files', 'Список пользователей': 'list_users', 'Список гостей': 'list_guests',
            'Статистика за сегодня': 'statistic_today', 'Статистика всех кнопок': 'statistic_all_tooday'}
        keyb = InlineKeyboardMarkup(row_width=1)
        for butt in settings_buttons:
            if await moderators_db.check_access_moderator(chat_id, 'access_to_state_tools', settings_buttons[butt]):
                inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
                keyb.add(inline_button)
        return keyb

    chat_id = message.from_user.id
    user_name = message.from_user.username
    text = "Cостояние бота:"
    keyboard = await start_menu_keyboard()

    await state.finish()
    await create_user_menu(chat_id=chat_id, user_name=user_name, text=text, keyboard=keyboard)


#  ----====  СПИСОК ПОЛЬЗОВАТЕЛЕЙ  ====----
@dp.callback_query_handler(text="Список пользователей", state='*')
async def users_all_users(call: types.CallbackQuery, state: FSMContext):
    def list_all_users():
        users_names = users_db.users_names
        num = len(users_names)
        users_names.sort(key=str.lower)
        users = ''
        for user in users_names:
            user_stat_name = ''
            if users_db.users[user].user_stat_name:
                user_stat_name = f' ({users_db.users[user].user_stat_name})'
            users += f'\n{user}{user_stat_name}'
        return f'Всего {num} пользователей:\n{users}'

    answer = list_all_users()
    await state.finish()
    await call.message.answer(answer)
    await call.answer()
    await log.write(f'admin_menu: список пользователей, ({call.from_user.username})')


#  ----====  СТАТИСТИКА ЗА СЕГОДНЯ  ====----
@dp.callback_query_handler(text="Статистика за сегодня", state='*')
async def users_tooday_statistic(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await stat_db.get_html()
    with open('statistic.html', 'rb') as file:
        await call.message.answer_document(file)
    await call.answer()
    await log.write(f'admin_menu: статистика за сегодня, ({call.from_user.username})')


#  ----====  ПОЛНАЯ СТАТИСТИКА ЗА СЕГОДНЯ  ====----
@dp.callback_query_handler(text="Статистика всех кнопок", state='*')
async def users_tooday_statistic(call: types.CallbackQuery, state: FSMContext):
    file_stat = 'all_butt_stat.html'

    await state.finish()
    await stat_db.get_html(get_all=True, file_stat=file_stat)
    with open(file_stat, 'rb') as file:
        await call.message.answer_document(file)
    await call.answer()
    await log.write(f'admin_menu: полная статистика за сегодня, ({call.from_user.username})')


@dp.callback_query_handler(text='Кнопки - группы - № блоков')
async def user_stat(call: types.CallbackQuery):
    def button_text(butt):
        button_name = buttons_db.buttons[butt].name
        num_text = ''
        button_groups = buttons_db.buttons[butt].group_buttons
        num_block = buttons_db.buttons[butt].num_block
        if num_block: num_text = f' - {num_block}'
        return f"• {button_name} - {button_groups}{num_text}\n"

    text = 'кнопка - группы - № блока\n'
    text_stat = ''
    text_not_stat = ''
    text_hidden = ''
    user_name = call.from_user.username

    for button in buttons_db.buttons:
        if buttons_db.buttons[button].hidden == 0:
            if buttons_db.buttons[button].statistical == 1:
                text_stat += button_text(button)
            else:
                text_not_stat += button_text(button)
        else:
            text_hidden += button_text(button)
    if text_stat:
        text += '\n    В статистике:\n' + text_stat
    if text_not_stat:
        text += '\n    Не в статистике:\n' + text_not_stat
    if text_hidden:
        text += '\n    Скрытые:\n' + text_hidden

    await call.message.answer(text)
    await log.write(f'admin_menu: Список кнопок ({user_name})')
    await call.answer()


@dp.callback_query_handler(text='Список файлов')
async def user_stat(call: types.CallbackQuery):
    stat = ''
    for file in f_db.files:
        length_file = await f_db.get_len_file(file)
        stat += f'{f_db.files[file].name} -- {f_db.files[file].num_line} из {length_file}\n'
    await call.message.answer(stat)
    await log.write(f'admin_menu: Список файлов, ({call.from_user.username})')
    await call.answer()


@dp.callback_query_handler(text='Список гостей')
async def user_stat(call: types.CallbackQuery):
    text = 'id - имя\n\n'
    if Guests.guests:
        for guest in Guests.guests:
            text += f"{guest} - {Guests.guests[guest]}\n"
        await call.message.answer(text)
    else:
        await call.message.answer('Гостей нет')
    await log.write(f'admin_menu: Список гостей, ({call.from_user.username})')
    await call.answer()


@dp.callback_query_handler(text='Кнопки - файлы - нажатия')
async def buttons_files(call: types.CallbackQuery):
    text = 'Кнопка - файл - осталось нажатий\n\n'
    for button in buttons_db.buttons:
        #  Количество оставшихся нажатий кнопки
        cliks = await get_button_clicks(button)
        if cliks:
            file = buttons_db.buttons[button].work_file
            name = buttons_db.buttons[button].name
            text += f"• {name} - {file} - {cliks}\n"
    await call.message.answer(text)
    await log.write(f'admin_menu: Кнопки - файлы, ({call.from_user.username})')
    await call.answer()
