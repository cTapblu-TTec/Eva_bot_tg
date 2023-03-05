from asyncio import sleep, create_task
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime

from aiogram import types
from aiogram.utils.exceptions import BadRequest

from loader import bot
from work_vs_db.db_adm_chats import adm_chats_db


@dataclass()
class Data:
    time_saved = {}


async def create_level_menu(chat_id: int, level: str, text: str, keyboard=None):
    if keyboard:
        msg = await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    else:
        msg = await bot.send_message(chat_id=chat_id, text=text)
    await adm_chats_db.write(chat_id=chat_id, tools=[level], values=[msg["message_id"]])


async def delete_last_menu(chat_id: int):
    levels = {'id_msg_settings': 1, 'id_msg_options': 2, 'id_msg_tools': 3, 'id_msg_values': 4}
    list_menus = []
    last = 'id_msg_settings'
    if chat_id in adm_chats_db.chats:
        chat = adm_chats_db.chats[chat_id]
        if chat is None: return
        for level in levels:
            if getattr(chat, level, None):
                list_menus.append(level)
        for level in list_menus:
            if levels[level] > levels[last]:
                last = level
        if last != 'id_msg_settings':
            await delete_old_message(chat_id, last)


async def delete_loue_level_menu(chat_id: int, type_menu: str):
    levels = {'id_msg_settings': 1, 'id_msg_options': 2, 'id_msg_tools': 3, 'id_msg_values': 4}
    for level in levels:
        if levels[level] >= levels[type_menu]:
            await delete_old_message(chat_id, level)


async def delete_old_message(chat_id: int, type_menu: str):
    if chat_id in adm_chats_db.chats:
        chat = adm_chats_db.chats[chat_id]
        if chat is None: return
        message_id = getattr(chat, type_menu, None)
        if message_id is None: return
        await adm_chats_db.write(chat_id=chat_id, tools=[type_menu], values=['None'])
        with suppress(BadRequest):
            create_task(bot.delete_message(chat_id=chat_id, message_id=message_id))


async def create_menu_back(chat_id, text="Создано меню 'Назад'"):
    if chat_id in adm_chats_db.chats:
        type_menu = 'id_msg_system'
        chat = adm_chats_db.chats[chat_id]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад', 'Настройки бота')
        if chat is None: return
        if not chat.menu_back:
            await adm_chats_db.write(chat_id=chat_id, tools=['menu_back', 'menu_cancel'], values=['true', 'false'])
            await delete_old_message(chat_id=chat_id, type_menu=type_menu)
            await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)


async def create_menu_cancel(chat_id, text="Создано меню 'Отмена'"):
    if chat_id in adm_chats_db.chats:
        type_menu = 'id_msg_system'
        chat = adm_chats_db.chats[chat_id]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена')
        if chat is None: return
        if not chat.menu_cancel:
            await adm_chats_db.write(chat_id=chat_id, tools=['menu_back', 'menu_cancel'], values=['false', 'true'])
            await delete_old_message(chat_id=chat_id, type_menu=type_menu)
            await create_level_menu(chat_id=chat_id, level=type_menu, text=text, keyboard=keyboard)


async def edit_message(chat_id: int, type_menu: str, keyboard=None, text: str = '⁣'):
    if chat_id in adm_chats_db.chats:
        chat = adm_chats_db.chats[chat_id]
        if chat is None: return
        message_id = getattr(chat, type_menu)
        if message_id is None: return
        with suppress(Exception):
            create_task(bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=keyboard, text=text))


async def delete_all_after_time(_chat_id: int, _time: int = 30):
    async def insert_def(chat_id: int, time: int):
        Data.time_saved[chat_id] = (datetime.now().hour*100 + datetime.now().minute)
        await sleep(60*time)  # ждем time минут
        time_now = datetime.now().hour*100 + datetime.now().minute
        if time_now >= Data.time_saved[chat_id] + time:
            types_m = ('id_msg_options', 'id_msg_tools', 'id_msg_values', 'id_msg_settings')
            for type_menu in types_m:
                await delete_old_message(chat_id, type_menu)

    create_task(insert_def(_chat_id, _time))
