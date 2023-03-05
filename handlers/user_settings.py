from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import ADMINS
from filters.users_filters import CallFilterUser
from loader import dp
from utils.admin_utils import get_button_clicks
from utils.log import log
from utils.user_utils import create_user_menu, delete_old_user_menu
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


class FCM(StatesGroup):
    waite_my_new_name = State()


@dp.message_handler(text='Мои настройки')
async def settings_button(message: types.Message):
    chat_id = message.from_user.id
    user_name = message.from_user.username
    text = "Мои настройки:"
    settings_buttons = ['Ваша статистика за сегодня', 'Описание кнопок', 'Скрыть клавиатуру', 'Много блоков за клик',
                        'Имя в статистике']
    keyboard = InlineKeyboardMarkup(row_width=1)
    for butt in settings_buttons:
        inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
        keyboard.add(inline_button)
    await create_user_menu(chat_id=chat_id, user_name=user_name, text=text, keyboard=keyboard)


@dp.callback_query_handler(text="Удалить имя")
async def user_blocks(call: types.CallbackQuery):
    user_name = call.from_user.username
    users_db.users[user_name].user_stat_name = None
    await users_db.write(user_name, ['user_stat_name'], [None])

    await call.message.answer(f'Имя удалено, теперь вы в статистике отображаетесь как "{user_name}"')
    await log.write(f'Имя удалено', user=user_name)
    await call.answer()


@dp.callback_query_handler(text='Имя в статистике')
async def user_blocks(call: types.CallbackQuery):
    chat_id = call.from_user.id
    username = call.from_user.username
    if users_db.users[username].user_stat_name:
        user_stat_name_text = f'Сейчас Ваше имя - "{users_db.users[username].user_stat_name}"'
    else:
        user_stat_name_text = f'Сейчас имя не задано, вы в статистике отображаетесь как "{username}"'
    text = 'Можете ввести себе имя для отображения в общей статистике, если у Вас несколько аккаунтов, ' \
           'используйте одно имя, и ваша статистика объеденится. ' + user_stat_name_text
    settings_buttons = ["Ввести имя", "Удалить имя"]

    keyboard = InlineKeyboardMarkup(row_width=1)
    for butt in settings_buttons:
        inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
        keyboard.add(inline_button)
    await create_user_menu(chat_id, username, text, keyboard=keyboard)
    await log.write(f'Имя в статистике', user=username)
    await call.answer()


@dp.callback_query_handler(text='Ввести имя')
async def user_blocks(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.from_user.id
    username = call.from_user.username
    text = 'Введите Ваше имя:'

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="Отмена"))
    await create_user_menu(chat_id=chat_id, user_name=username, text=text, keyboard=keyboard)
    await state.set_state(FCM.waite_my_new_name.state)
    await log.write(f'Ввести имя', user=username)
    await call.answer()


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_my_new_name)
async def button_read_value(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    new_name = new_name.lstrip('@')
    iskl = ' !"$%&()*+,/:;<>=?@^#{}|~'
    begin = True

    await state.finish()
    for i in iskl:
        if i in new_name:
            begin = False
    if new_name == '' or len(new_name) > 15:
        begin = False
    if not begin:
        await message.answer('Недопустимое имя')
        return
    user_name = message.from_user.username
    users_db.users[user_name].user_stat_name = new_name
    await users_db.write(user_name, ['user_stat_name'], [new_name])
    await message.answer(f'Установлено имя "{new_name}"')
    await log.write(f'Установлено имя "{new_name}"', user=user_name)


@dp.callback_query_handler(text='Много блоков за клик')
async def user_blocks(call: types.CallbackQuery):
    chat_id = call.from_user.id
    username = call.from_user.username
    use = users_db.users[username].use_many_blocks

    text = 'Использовать выдачу по несколько блоков'
    keyboard = InlineKeyboardMarkup(row_width=1)
    if use == 0:
        but = InlineKeyboardButton(text='Включить', callback_data='u_blocks/1')
    else:
        but = InlineKeyboardButton(text='Выключить', callback_data='u_blocks/0')
    keyboard.row(but)

    await create_user_menu(chat_id=chat_id, user_name=username, text=text, keyboard=keyboard)
    await log.write(f'Много блоков за клик', user=call.from_user.username)
    await call.answer()


@dp.callback_query_handler(CallFilterUser(startswith='u_blocks'))
async def user_blocks(call: types.CallbackQuery):
    query = call.data.split('/')
    use = int(query[1])
    username = call.from_user.username
    chat_id = call.from_user.id
    await delete_old_user_menu(chat_id, username)
    if use == 1:
        users_db.users[username].use_many_blocks = use
        text = 'Теперь будет запрос количества перед выдачей блока'
    else:
        users_db.users[username].use_many_blocks = use
        text = 'Будет выдаваться по одному блоку'
    await users_db.write(username, ['use_many_blocks'], [use])
    await call.message.answer(text)
    await log.write(f'{text}', user=username)
    await call.answer()


@dp.callback_query_handler(text='Ваша статистика за сегодня')
async def user_stat(call: types.CallbackQuery):
    user_name = call.from_user.username
    statistic = await stat_db.get_personal_stat(user_name)
    if statistic:
        await call.message.answer(statistic)
    else:
        await call.message.answer('Вы сегодня ничего не брали')
    await log.write(f'Личная статистика', user=user_name)
    await call.answer()


@dp.callback_query_handler(text='Описание кнопок')
async def user_stat(call: types.CallbackQuery):
    def button_text(butt):
        button_name = buttons_db.buttons[butt].name
        button_specification = buttons_db.buttons[butt].specification
        button_cliks = ''
        if cliks: button_cliks = f' ({cliks})'
        return f"• {button_name}{button_cliks} - {button_specification}\n"

    def button_is_available(butt, user):
        is_available_user = False
        button_in_available_group = False
        list_available_grous = []
        for group in buttons_db.buttons_groups:
            if groups_db.groups[group].hidden == 0 or \
                    (groups_db.groups[group].users and user in groups_db.groups[group].users):
                list_available_grous.append(group)
        for group in list_available_grous:
            if buttons_db.buttons[button].group_buttons and group in buttons_db.buttons[butt].group_buttons:
                button_in_available_group = True
        if buttons_db.buttons[butt].hidden == 0 or \
                (buttons_db.buttons[butt].users and user in buttons_db.buttons[butt].users):
            is_available_user = True
        if button_in_available_group and is_available_user:
            return True
        else:
            return False

    text = 'кнопка (осталось нажатий) - описание:\n'
    text_stat = ''
    text_not_stat = ''
    user_name = call.from_user.username
    is_admin = call.message.chat.id in ADMINS

    for button in buttons_db.buttons:
        if button_is_available(button, user_name) or (is_admin and buttons_db.buttons[button].hidden == 0):
            cliks = await get_button_clicks(button)
            if buttons_db.buttons[button].statistical == 1:
                text_stat += button_text(button)
            else:
                text_not_stat += button_text(button)
    if text_stat:
        text += '\nКнопки, которые идут в статистику:\n' + text_stat
    if text_not_stat:
        text += '\nКнопки, которые не идут в статистику:\n' + text_not_stat
    if is_admin:
        text += '\nСкрытые кнопки:\n'
        for button in buttons_db.buttons:
            if buttons_db.buttons[button].hidden == 1:
                cliks = await get_button_clicks(button)
                text += button_text(button)
    await call.message.answer(text)
    await log.write(f'Описание кнопок', user=user_name)
    await call.answer()


@dp.callback_query_handler(text='Скрыть клавиатуру')
async def dell_menu(call: types.CallbackQuery):
    await call.message.answer('Клавиатура удалена', reply_markup=types.ReplyKeyboardRemove())
    await log.write(f'Клавиатура удалена', user=call.from_user.username)
    await call.answer()
