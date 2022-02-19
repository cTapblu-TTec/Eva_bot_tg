from aiogram import types

from loader import dp


async def set_default_commands():
    await dp.bot.set_my_commands(
        [
            types.BotCommand("shablon", "Для топа"),
            types.BotCommand("otmetki", "Для отметок по 5"),
            types.BotCommand("storis", "Для сторис"),
            types.BotCommand("vk", "Для ВК"),
        ]
    )
