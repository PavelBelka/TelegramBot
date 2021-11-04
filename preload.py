import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db.Database import Database

loop = asyncio.get_event_loop()
print(loop.get_debug())
new_bot = Bot(token="2008283464:AAGD8GA-sDC2jYEAypOs-PKTsym3wm2yx_c")
storage = MemoryStorage()
dp = Dispatcher(new_bot, storage=storage, loop=loop)
db = Database()