from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from filters.users_filters import FilterForAskHowManyBlocks, CallFilterUser, FilterForGeneral
from utils.general import general
from loader import dp
from utils.user_utils import create_user_menu, delete_old_user_menu


@dp.message_handler(FilterForAskHowManyBlocks())
async def ask_how_many_blocks(message: types.Message):
    chat_id = message.from_user.id
    user_name = message.from_user.username
    button = message.text
    but = []
    text = f'{button} - cколько блоков?'
    keyboard = InlineKeyboardMarkup(row_width=1)
    for i in range(10):
        but.append(InlineKeyboardButton(text=str(i+1), callback_data=f'ask_blocks/{button}/{i + 1}'))
    keyboard.row(but[0], but[1], but[2], but[3], but[4])
    keyboard.row(but[5], but[6], but[7], but[8], but[9])
    await create_user_menu(chat_id=chat_id, user_name=user_name, text=text, keyboard=keyboard)


@dp.callback_query_handler(CallFilterUser(startswith='ask_blocks'))
async def user_blocks(call: types.CallbackQuery):
    query = call.data.split('/')
    button = query[1]
    blocks = int(query[2])
    username = call.from_user.username
    chat_id = call.from_user.id
    await delete_old_user_menu(chat_id=chat_id, user_name=username)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Назад', button + ' Х' + str(blocks)])

    await general(button, username, chat_id, blocks)
    await call.answer()


@dp.message_handler(FilterForGeneral())
async def general_hendler(message: types.Message):
    await general(message.text, message.from_user.username, message.from_user.id)
