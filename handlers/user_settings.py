from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import ADMINS
from filters.users_filters import CallFilterForBlocksUser
from loader import dp
from utils.admin_utils import get_button_clicks
from utils.log import log
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


class FCM(StatesGroup):
    waite_user_name = State()


async def list_groups(user, admin):
    not_hidden_groups = []
    hidden_groups = []
    for group in buttons_db.buttons_groups:
        if groups_db.groups[group].hidden == 0:
            not_hidden_groups.append(group)
        elif (groups_db.groups[group].users and user in groups_db.groups[group].users) or admin:
            hidden_groups.append(group)
    return not_hidden_groups, hidden_groups


@dp.callback_query_handler(text='Волонтерство')
async def groups_list(call: types.CallbackQuery):
    username = call.from_user.username
    is_admin = call.message.chat.id in ADMINS
    not_hidden_groups, hidden_groups = await list_groups(username, is_admin)

    keyboard = InlineKeyboardMarkup(row_width=1)
    for group in (not_hidden_groups + hidden_groups):
        keyboard.add(InlineKeyboardButton(text=f'{group} - {groups_db.groups[group].specification}\n',
                                          callback_data=('menu_groups/'+group)))

    await call.message.answer("Группы кнопок для волонтерства:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text='Дополнительные функции')
async def settings_button(call: types.CallbackQuery):

    settings_buttons = ['Ваша статистика за сегодня', 'Описание кнопок', 'Скрыть клавиатуру', 'Много блоков за клик',
                        'Имя в статистике']
    keyboard = InlineKeyboardMarkup(row_width=1)
    for butt in settings_buttons:
        inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
        keyboard.add(inline_button)
    await call.message.answer("Дополнительные функции:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text="Удалить имя")
async def user_blocks(call: types.CallbackQuery):
    username = call.from_user.username
    user_name = call.from_user.username
    users_db.users[user_name].user_stat_name = None
    await users_db.write(user_name, ['user_stat_name'], [None])
    await call.message.answer(f'Имя удалено, теперь вы в статистике отображаетесь как "{username}"')


@dp.callback_query_handler(text='Имя в статистике')
async def user_blocks(call: types.CallbackQuery):
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
    await call.message.answer(text, reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text='Ввести имя')
async def user_blocks(call: types.CallbackQuery, state: FSMContext):
    text = 'Введите Ваше имя:'

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="Отмена"))
    await call.message.answer(text, reply_markup=keyboard)
    await state.set_state(FCM.waite_user_name.state)
    await call.answer()


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_user_name)
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


@dp.callback_query_handler(text='Много блоков за клик')
async def user_blocks(call: types.CallbackQuery):
    but = []
    text = 'Тут можно выбрать сколько блоков за одно нажатие кнопки будет выдаваться'
    keyboard = InlineKeyboardMarkup(row_width=1)
    for i in range(10):
        but.append(InlineKeyboardButton(text=str(i+1), callback_data=('u_blocks/' + str(i+1))))
    keyboard.row(but[0], but[1], but[2], but[3], but[4])
    keyboard.row(but[5], but[6], but[7], but[8], but[9])
    await call.message.answer(text, reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(CallFilterForBlocksUser())
async def user_blocks(call: types.CallbackQuery):
    def block_text(block):
        if block == 1:
            return "по 1 блоку"
        if 2 <= block <= 4:
            return f"сразу по {block} блока"
        else:
            return f"сразу по {block} блоков"
    query = call.data.split('/')
    blocks = int(query[1])
    username = call.from_user.username
    users_db.users[username].blocks = blocks
    bl_text = block_text(blocks)
    text = 'Теперь Вам будет выдаваться ' + bl_text
    await users_db.write(username, ['blocks'], [blocks])
    await call.message.answer(text)
    await call.answer()


@dp.callback_query_handler(text='Ваша статистика за сегодня')
async def user_stat(call: types.CallbackQuery):

    user_name = call.from_user.username
    head = 'Ваша статистика за сегодня:\nКнопка - нажатий\n'
    statistic = await stat_db.get_personal_stat(user_name)
    await call.message.answer(head + statistic)
    await log.write(f'Личная статистика, ({user_name})')
    await call.answer()


@dp.callback_query_handler(text='Описание кнопок')
async def user_stat(call: types.CallbackQuery):
    text = 'кнопка (осталось нажатий) - описание:\n'
    user_name = call.from_user.username

    for button in buttons_db.buttons:
        cliks = await get_button_clicks(button)
        if buttons_db.buttons[button].hidden == 0 or \
                (buttons_db.buttons[button].users and user_name in buttons_db.buttons[button].users):
            button_name = buttons_db.buttons[button].name
            button_specification = buttons_db.buttons[button].specification
            button_cliks = ''
            if cliks: button_cliks = f' ({cliks})'
            text += f"• {button_name}{button_cliks} - {button_specification}\n"
    if call.message.chat.id in ADMINS:
        text += '\nскрытые кнопки:\n'
        for button in buttons_db.buttons:
            cliks = await get_button_clicks(button)
            if buttons_db.buttons[button].hidden == 1:
                button_name = buttons_db.buttons[button].name
                button_specification = buttons_db.buttons[button].specification
                button_cliks = ''
                if cliks: button_cliks = f'({cliks})'
                text += f"• {button_name}{button_cliks} - {button_specification}\n"
    await call.message.answer(text)
    await log.write(f'Описание кнопок, ({user_name})')
    await call.answer()


@dp.callback_query_handler(text='Скрыть клавиатуру')
async def dell_menu(call: types.CallbackQuery):
    await call.message.answer('клавиатура удалена', reply_markup=types.ReplyKeyboardRemove())
    await log.write(f'клавиатура удалена, ({call.from_user.username})')
    await call.answer()
