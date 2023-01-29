from asyncio import sleep, create_task
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime

from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from loader import dp
from work_vs_db.db_adm_chats import adm_chats_db


@dataclass()
class Data:
    time_saved: int


async def dellete_old_message(chat_id: int, type_menu: str):
    if chat_id in adm_chats_db.chats:
        chat = adm_chats_db.chats[chat_id]
        if chat is None: return
        message_id = getattr(chat, type_menu, None)
        if message_id is None: return
        await adm_chats_db.write(chat_id=chat_id, tools=[type_menu], values=['None'])
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            create_task(dp.bot.delete_message(chat_id=chat_id, message_id=message_id))


async def create_menu_back(chat_id, text="Создано меню 'Назад'"):
    if chat_id in adm_chats_db.chats:
        chat = adm_chats_db.chats[chat_id]
        if chat is None: return
        if not chat.menu_back:
            await adm_chats_db.write(chat_id=chat_id, tools=['menu_back', 'menu_cancel'], values=['true', 'false'])
            create_task(dp.bot.send_message(chat_id=chat_id, text=text,
                                      reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад',
                                                                                                       '/settings')))


async def create_menu_cancel(chat_id, text="Создано меню 'Отмена'"):
    if chat_id in adm_chats_db.chats:
        chat = adm_chats_db.chats[chat_id]
        if chat is None: return
        if not chat.menu_cancel:
            await adm_chats_db.write(chat_id=chat_id, tools=['menu_back', 'menu_cancel'], values=['false', 'true'])
            create_task(dp.bot.send_message(chat_id=chat_id, text=text,
                                      reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена')))


async def edit_message(chat_id: int, type_menu: str, keyboard=None, text: str = '⁣'):
    if chat_id in adm_chats_db.chats:
        chat = adm_chats_db.chats[chat_id]
        if chat is None: return
        message_id = getattr(chat, type_menu)
        if message_id is None: return
        with suppress():
            create_task(dp.bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=keyboard, text=text))


async def delete_all_after_time(chat_id: int, time: int = 30):
    Data.time_saved = datetime.now().hour*100 + datetime.now().minute
    await sleep(60*time)  # ждем time минут
    time_now = datetime.now().hour*100 + datetime.now().minute
    if time_now >= Data.time_saved + time:
        types_m = ('id_msg_options', 'id_msg_tools', 'id_msg_values', 'id_msg_settings')
        for type_menu in types_m:
            await dellete_old_message(chat_id, type_menu)
