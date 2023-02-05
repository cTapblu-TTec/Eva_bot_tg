from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import ADMINS
from loader import dp
from utils.admin_utils import get_button_clicks
from utils.log import log
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_stat import stat_db


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
    is_admin = str(call.message.chat.id) in ADMINS
    not_hidden_groups, hidden_groups = await list_groups(username, is_admin)

    keyboard = InlineKeyboardMarkup(row_width=1)
    for group in (not_hidden_groups + hidden_groups):
        keyboard.add(InlineKeyboardButton(text=f'{group} - {groups_db.groups[group].specification}\n',
                                          callback_data=('menu_groups/'+group)))

    await call.message.answer("Группы кнопок для волонтерства:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text='Дополнительные функции')
async def settings_button(call: types.CallbackQuery):

    settings_buttons = ['Ваша статистика за сегодня', 'Описание кнопок', 'Удалить кнопки']
    keyboard = InlineKeyboardMarkup(row_width=1)
    for butt in settings_buttons:
        inline_button = InlineKeyboardButton(text=butt, callback_data=butt)
        keyboard.add(inline_button)
    await call.message.answer("Дополнительные функции:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text='Ваша статистика за сегодня')
async def user_stat(call: types.CallbackQuery):

    user_name = call.from_user.username
    head = 'Ваша статистика за сегодня:\nКнопка - нажатий\n'
    statistic = await stat_db.get_personal_stat(user_name)
    await call.message.answer(head + statistic)
    await log.write(f'Личная статистика, ({user_name})\n')
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
    if str(call.message.chat.id) in ADMINS:
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
    await log.write(f'Описание кнопок, ({user_name})\n')
    await call.answer()


@dp.callback_query_handler(text='Удалить кнопки')
async def dell_menu(call: types.CallbackQuery):
    await call.message.answer('клавиатура удалена', reply_markup=types.ReplyKeyboardRemove())
    await call.answer()
