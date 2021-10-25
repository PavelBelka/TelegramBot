import logging
from aiogram import Bot, Dispatcher, executor
from psycopg_pool import AsyncConnectionPool
from db.Database import Database

if __name__ == 'main':
    logging.basicConfig(level=logging.INFO)
    new_bot = Bot(token="2008283464:AAFvmqKxp6XJQhGD7cKx2VE55FBKo6qV628")
    dp = Dispatcher(new_bot)
    pool = AsyncConnectionPool(min_size=1, max_size=20, kwargs={"user": "telefinbot",
                                                                "password": "Yakov2020",
                                                                "host": "localhost",
                                                                "dbname": "FinBot"})
    db = Database()
    #telegram = TelegramBot(dp, new_bot)
    #telegram.message_register()
    executor.start_polling(dp, skip_updates=True)