import asyncio
import logging
import asyncpg
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.config import LINUX, DATABASE_URL
from filters.chek_buttons import ChekButtons, ChekGroupButtons, ChekButtonsForCallback
from loader import dp
from middlewares.menu import MenuMid
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.reset import reset_statistics
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_files_id import files_id_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db

logger = logging.getLogger(__name__)


async def on_startup():
    # Устанавливаем дефолтные команды
    await set_default_commands()
    # Уведомляет про запуск
    await on_startup_notify()


def create_pool() -> asyncpg.Pool:
    if LINUX:
        return asyncpg.create_pool(database='eva', user='bot', password='vga1600', host='localhost', max_size=20)
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
    scheduler.timezone = timezone('Europe/Moscow')
    scheduler.add_job(reset_statistics, 'cron', hour=2, minute=30, misfire_grace_time=3600)
    # _________POOL________
    pool = await create_pool()
    await users_db.create(pool)
    await files_id_db.create(pool)
    await f_db.create(pool)
    await stat_db.create(pool)
    await buttons_db.init(pool)
    await groups_db.create(pool)

    # _________START BOT________
    dp.middleware.setup(MenuMid())
    dp.filters_factory.bind(ChekButtons)
    dp.filters_factory.bind(ChekGroupButtons)
    dp.filters_factory.bind(ChekButtonsForCallback)
    import handlers
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
        if not LINUX:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
