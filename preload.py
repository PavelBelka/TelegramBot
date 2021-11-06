import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db.Database import Database
from configuration import config

loop = asyncio.get_event_loop()
new_bot = Bot(token=str(config.BOT_TOKEN))
storage = MemoryStorage()
dp = Dispatcher(new_bot, storage=storage, loop=loop)
db = Database()