import logging, sys, asyncio, os
from psycopg_pool import AsyncConnectionPool
from aiogram import executor

os.environ['PYTHONASYNCIODEBUG'] = '1'

async def database_startup(dbs):
    pool = AsyncConnectionPool(min_size=1, max_size=20, kwargs={"user": "telefinbot",
                                                                "password": "Yakov2020",
                                                                "host": "localhost",
                                                                "dbname": "FinBot",
                                                                "autocommit": "True"})
    dbs.create_pool(pool)

async def on_startup(dp):
    import middleware
    print("Start program...")
    middleware.setup(dp)

async def on_shutdown(dbs, bot, dispatcher):
    print("Start process shutdown....")
    dispatcher.stop_polling()
    await dispatcher.wait_closed()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    await dbs.delete_pool()
    await bot.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if sys.platform == "win32" and sys.version_info.minor >= 8:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        from preload import loop, new_bot
        from app.handlers import dp, db
        loop.create_task(database_startup(db))
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    finally:
        loop.run_until_complete(on_shutdown(db, new_bot, dp))
        loop.stop()
        loop.close()