from aiogram import types

from utils.Proverka import prover
from loader import dp


@dp.message_handler(commands=['b'])
async def bot_echo(message: types.Message):
    user = await prover(message, 'other')  # проверяем статус пользователя
    if user == "guest": return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = '/st'
    keyboard.add(buttons)
    buttons = ["/vk_id", "/vk_http"]
    keyboard.add(*buttons)
    buttons = ["/vk_club", "/vk_lots"]
    keyboard.add(*buttons)

    await message.answer("для сторис ВК (9), нажми /vk_id \n "
                         "10 отметок людей, нажми /vk_http \n "
                         "10 групп, нажми /vk_club \n "
                         "10 лотерей, нажми /vk_lots\n"
                         "после каждой команды через пробел можно указать число от 1 до 10 - сколько блоков выдать"
                         , reply_markup=keyboard)


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    user = await prover(message, 'other')  # проверяем статус пользователя
    if user == "guest": return

    if user == 'admin':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["/admin", "/gena"]
        keyboard.add(*buttons)
        buttons = ["/gor_stor", "/gor_shab"]
        keyboard.add(*buttons)
        buttons = ["/otmetki", "/shablon"]
        keyboard.add(*buttons)
        buttons = ["/storis", "/vk"]
        keyboard.add(*buttons)

        await message.answer("Привет, я Ева!\n "
                             "Для топа, нажми /shablon\n "
                             "Для отметок по 5, нажми /otmetki\n "
                             "Для сторис, нажми /storis\n "
                             "Для ВК, нажми /vk\n"
                             "Чтобы вернуть отметки нажми /vern\n"
                             "/admin - админские команды\n"
                             "/b - дополнительные функции", reply_markup=keyboard)

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["/gor_stor", "/gor_shab"]
        keyboard.add(*buttons)
        buttons = ["/otmetki", "/shablon"]
        keyboard.add(*buttons)
        buttons = ["/storis", "/vk"]
        keyboard.add(*buttons)

        await message.answer("Привет, я Ева! \n "
                             "Для топа, нажми /shablon \n "
                             "Для отметок по 5, нажми /otmetki \n "
                             "Для сторис, нажми /storis \n "
                             "Для ВК, нажми /vk \n"
                             "Чтобы вернуть отметки нажми /vern", reply_markup=keyboard)
