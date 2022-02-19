import asyncio
import logging
import asyncpg
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import handlers
from data.config import HEROKU, DATABASE_URL
from loader import dp
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.reset import reset_statistics
from work_vs_db.db_files import files_db
from work_vs_db.db_statistic import stat_db
from work_vs_db.db_users import users_db
from work_vs_db.db_vars import vars_db

logger = logging.getLogger(__name__)


async def on_startup():
    # Устанавливаем дефолтные команды
    await set_default_commands()
    # Уведомляет про запуск
    await on_startup_notify()


def create_pool() -> asyncpg.Pool:
    if HEROKU:
        return asyncpg.create_pool(DATABASE_URL, max_size=20)
    else:
        return asyncpg.create_pool(database='abc', user='postgres', password='vga1600', host='localhost', max_size=20)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    # _________SCHEDULER________
    scheduler = AsyncIOScheduler()
    scheduler.timezone = pytz.timezone('Europe/Moscow')
    scheduler.add_job(reset_statistics, 'cron', hour=2, minute=30)
    # _________POOL________
    pool = await create_pool()
    await users_db.create(pool)
    await vars_db.create(pool)
    await stat_db.create(pool)
    await files_db.create(pool)


    # _________START BOT________
    await on_startup()
    await dp.skip_updates()
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        dp.stop_polling()
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await dp.bot.get_session()
        await session.close()

    # _________MAIN________
if __name__ == '__main__':
    try:
        if not HEROKU:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
