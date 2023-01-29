from dataclasses import dataclass
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext

from filters.callback_filters import ChekGroupsForCallback, ChekDellGroup, CallbackGroupValueFilter
from utils.admin_menu_utils import dellete_old_message, create_menu_back, create_menu_cancel, edit_message, \
    delete_all_after_time
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp
from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_users import users_db


@dataclass()
class Data:
    query = {}
    tools_g = []
    names_tools = {'name': 'Имя группы', 'hidden': 'Скрытая группа (1/0)', 'users': 'Кому доступ скрытой',
                   'specification': 'Описание'}


class FCM(StatesGroup):
    waite_tool_group = State()
    waite_value_group = State()


async def groups_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for group in groups_db.groups:
        keyboard.add(InlineKeyboardButton(text=f'Настройка группы "{group}"', callback_data=group))
    keyboard.add(InlineKeyboardButton(text='Про добавление групп', callback_data='add_group'))
    return keyboard


async def tools_gr_keyboard(group):
    keyboard = InlineKeyboardMarkup(row_width=1)
    Data.tools_g = [a for a in dir(groups_db.groups[group]) if not a.startswith('__')]
    for tool in Data.tools_g:
        value = getattr(groups_db.groups[group], tool, None)
        if tool in Data.names_tools:
            tool_text = Data.names_tools[tool]
            c_data = f'gr_value/{group}/{tool}'
            # print(len(c_data.encode('utf-8')))
            inline_button = InlineKeyboardButton(text=f'{tool_text} --==-- {value}', callback_data=c_data)
            keyboard.add(inline_button)
    keyboard.add(InlineKeyboardButton(text='Удалить группу', callback_data='dell_group/' + group))
    return keyboard


#  ----====  ВЫБОР ГРУППЫ  ====----
@dp.callback_query_handler(text="Настройка групп", state='*')
async def settings_groups(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_options')
    # id_msg_options
    keyboard = await groups_keyboard()
    msg = await call.message.answer("Настройка групп кнопок:", reply_markup=keyboard)

    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_options'], values=[msg["message_id"]])
    await call.answer()
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    await delete_all_after_time(call.message.chat.id)


#  ----====  ДОБАВИТЬ ГРУППУ ====----
@dp.callback_query_handler(text='add_group', state='*')
async def add_group(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("Группы добавляются автоматически, когда вносятся в Настройки кнопки - Меню кнопок. "
                              "Кнопку можно добавить в несколько групп, указав их в 'Меню кнопок' через запятые.")
    await call.answer()


#  ----====  УДАЛИТЬ ГРУППУ ====----
@dp.callback_query_handler(ChekDellGroup(), state='*')
async def dell_group(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    group = call.data.split('/')[1]

    if group in groups_db.groups:
        await groups_db.write(group, 'dell_group', '')
        for button in buttons_db.buttons:
            if group in buttons_db.buttons[button].group_buttons:
                groups_batt = buttons_db.buttons[button].group_buttons.replace(group, '')
                await buttons_db.write(button, ["group_buttons"], [groups_batt])

        for user in users_db.users:
            if group == users_db.users[user].menu:
                await users_db.write(user, ['menu'], [None])
                users_db.users[user].menu = None

        await edit_message(chat_id=call.message.chat.id,
                           type_menu='id_msg_options',
                           keyboard=(await groups_keyboard()),
                           text=f"Группа {group} удалена")
        await call.message.answer(f"Группа {group} удалена")
        await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    else:
        await call.message.answer(f"Группа {group} не найдена")
    await call.answer()
    await log.write(f"admin: Группа {group} удалена ({call.message.chat.username})\n")
    await delete_all_after_time(call.message.chat.id)


#  ----====  ВЫБОР ПАРАМЕТРА ГРУППЫ  ====----
@dp.callback_query_handler(ChekGroupsForCallback(), state="*")
async def settings_group_tool(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_back(call.message.chat.id)
    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_tools')
    # id_msg_tools
    group = call.data
    keyboard = await tools_gr_keyboard(group)
    msg = await call.message.answer(f"Выберите параметр группы '{group}' для настройки:", reply_markup=keyboard)
    await adm_chats_db.write(chat_id=call.message.chat.id, tools=['id_msg_tools'], values=[msg["message_id"]])
    await call.answer()

    await dellete_old_message(chat_id=call.message.chat.id, type_menu='id_msg_values')
    await delete_all_after_time(call.message.chat.id)


#  ----====  ЗАПРОС ЗНАЧЕНИЯ  ====----
@dp.callback_query_handler(CallbackGroupValueFilter())
async def settings_group_value(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await create_menu_cancel(call.message.chat.id)
    # id_msg_value
    # START HANDLER
    if '/' in call.data[1:]:
        query = call.data.split('/')
        group = query[1]
        tool = query[2]
    else:
        await call.message.answer(f"Что-то в группах пошло не так, нажмите /settings")
        await log.write(f"admin: Что-то в группах пошло не так, call.data: '{call.data}' ({call.from_user.username})\n")
        return

    if tool not in Data.tools_g:
        await call.message.answer(f"Выберите параметр группы '{group}' для настройки")
        return

    Data.query = {'group': group, 'tool': tool}

    # FINISH HANDLER
    tool_text = Data.names_tools[tool]
    await call.message.answer(f"Введите значение параметра '{tool_text}' для группы '{group}'")
    await state.set_state(FCM.waite_value_group.state)
    await call.answer()
    await delete_all_after_time(call.message.chat.id)


#  ----====  ЧТЕНИЕ ЗНАЧЕНИЯ  ====----
@dp.message_handler(state=FCM.waite_value_group)
async def settings_group_value_read(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Отмена':
        await create_menu_back(message.chat.id)
        return

    # START HANDLER
    group = Data.query['group']
    tool = Data.query['tool']
    value = message.text
    tool_text = Data.names_tools[tool]

    try:
        await groups_db.write(group, [tool], [value])
        if tool == 'name':
            for button in buttons_db.buttons:
                if group in buttons_db.buttons[button].group_buttons:
                    groups_batt = buttons_db.buttons[button].group_buttons.replace(group, value)
                    await buttons_db.write(button, ["group_buttons"], [groups_batt])

            for user in users_db.users:

                if group == users_db.users[user].menu:
                    await users_db.write(user, ['menu'], [value])
                    users_db.users[user].menu = value

        if tool in ["name", "hidden", "users"]:
            await buttons_db.create()
            await groups_db.create(None)
            await message.answer("Данные обновлены из базы данных")

        await create_menu_back(chat_id=message.chat.id,
                               text=f"Значение '{value}' параметра '{tool_text}' для группы '{group}' установлено.")

        if tool == "name":
            group_name = value
            await edit_message(chat_id=message.chat.id,
                               type_menu='id_msg_options',
                               keyboard=(await groups_keyboard()),
                               text=f"Группа {group} переименована")

        else:
            group_name = group
        #  Обновление сообщения с tools
        await edit_message(chat_id=message.chat.id,
                           type_menu='id_msg_tools',
                           keyboard=(await tools_gr_keyboard(group_name)),
                           text=f"Значение '{value}' параметра '{tool_text}' для группы '{group}' установлено.")

        await log.write(f"admin: Значение '{value}' параметра '{tool_text} ({tool})' для группы '{group}' установлено,"
                  f" ({message.from_user.username})\n")

    except SystemExit:
        await message.answer(f"Значение '{value}' параметра '{tool_text}' для группы '{group}' не установлено!\n"
                             f"Введите новое значение")
        await state.set_state(FCM.waite_value_group.state)

        await log.write(f"admin: Значение '{value}' параметра '{tool_text} ({tool})' для группы '{group}' "
                        f"НЕ установлено!, ({message.from_user.username})\n")
