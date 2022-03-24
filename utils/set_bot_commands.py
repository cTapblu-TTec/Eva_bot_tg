from loader import dp


async def set_default_commands():
    await dp.bot.delete_my_commands()
