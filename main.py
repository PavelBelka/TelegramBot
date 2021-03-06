import logging, sys, asyncio
from psycopg_pool import AsyncConnectionPool
from aiogram import executor
from configuration import config

async def database_startup(dbs):
    pool = AsyncConnectionPool(min_size=1, max_size=20, kwargs={"user": config.PGUSER,
                                                                "password": config.PGPASSWORD,
                                                                "host": config.PGHOST,
                                                                "dbname": config.PGDBNAME,
                                                                "port": config.PGPORT,
                                                                "autocommit": "True"})
    dbs.create_pool(pool)

async def on_startup(dp):
    import middleware
    middleware.setup(dp)

async def on_shutdown(dbs, bot, dispatcher):
    dispatcher.stop_polling()
    await dispatcher.wait_closed()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    await dbs.delete_pool()
    await bot.close()

if __name__ == '__main__':
    logging.basicConfig(handlers=(logging.FileHandler('log.txt'), logging.StreamHandler()),
                        level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
    logger = logging.getLogger(__name__)
    logger.info("----Start program----")
    if sys.platform == "win32" and sys.version_info.minor >= 8:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        from preload import loop, new_bot
        from app import dp, db
        loop.create_task(database_startup(db))
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    finally:
        logger.info("----Start process shutdown----")
        loop.run_until_complete(on_shutdown(db, new_bot, dp))
        loop.stop()
        loop.close()