import asyncio
import logging

import asyncpg
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.config import LINUX, DB_HOST, DB_NAME, DB_USER, DB_PASS, ADMINS
from filters.moder_filter import registry_moder_filters
from filters.users_filters import registry_user_filters
from filters.admin_filters import registry_admin_filters
from loader import dp
from middlewares.menu import MenuMid
from utils.admin_menu_utils import delete_loue_level_menu
from utils.log import log
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.admin_utils import reset_statistics
from work_vs_db.db_moderators import moderators_db
from work_vs_db.manager_bd import init_bd

logger = logging.getLogger(__name__)


def logging_set_config():
    formatt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(level=logging.WARNING, format=formatt)

    loggerr = logging.getLogger()
    handler2 = logging.FileHandler('log.log')
    handler2.setFormatter(logging.Formatter(formatt))
    loggerr.addHandler(handler2)


async def on_startup():
    # Устанавливаем дефолтные команды
    await set_default_commands()
    # Уведомляет про запуск
    await on_startup_notify()
    # удаляем старые меню
    for admin in ADMINS:
        await delete_loue_level_menu(admin, 'id_msg_options')
    for moder in moderators_db.moderators:
        await delete_loue_level_menu(moder, 'id_msg_options')


def create_pool() -> asyncpg.Pool:
    if LINUX:
        return asyncpg.create_pool(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, max_size=20)
    else:
        return asyncpg.create_pool(database='abc', user='postgres', password='vga1600', host='localhost', max_size=20)


async def main():
    logging_set_config()

    # _________SCHEDULER________
    scheduler = AsyncIOScheduler()
    scheduler.timezone = timezone('Europe/Moscow')
    scheduler.add_job(reset_statistics, 'cron', hour=2, minute=30, misfire_grace_time=3600)

    # _________POOL________
    await init_bd(await create_pool())

    # _________START BOT________
    dp.middleware.setup(MenuMid())
    registry_admin_filters(dp)
    registry_user_filters(dp)
    registry_moder_filters(dp)
    import handlers
    await on_startup()
    await dp.skip_updates()
    try:
        scheduler.start()
        logger.warning("Starting bot")
        await dp.start_polling()
    finally:
        await log.send_log_now()
        dp.stop_polling()
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await dp.bot.get_session()
        await session.close()

    # _________MAIN________
if __name__ == '__main__':
    try:
        if not LINUX:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped!")
