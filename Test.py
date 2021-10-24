import asyncio
import logging
import os
import sys

from db.Database import Database
from psycopg_pool import AsyncConnectionPool

os.environ['PYTHONASYNCIODEBUG'] = '1'

logging.basicConfig(level=logging.DEBUG)

categories = ("Common", "Food", "Transport", "Utilities", "Salary")

async def main():
    print("Создал...")
    pool = AsyncConnectionPool(min_size=1, max_size= 20, kwargs={"user": "telefinbot",
                                                                 "password": "Yakov2020",
                                                                 "host": "localhost",
                                                                 "dbname": "FinBot"})
    test = Database()
    connect = await pool.getconn()
    cur = test.create_cursor(connect)
    verify = await test.verify_table(cur, 'test2')
    if verify:
        print("Таблица уже создана")
        data = await test.select_records_date(cur, 'test2', "2021-10-19 18:38:45.159014", "2021-10-19 18:38:49.186781")
        #test.update_record(cur, 'test', datetime.datetime.strptime("2021-10-19 18:38:45.159014", '%Y-%m-%d %H:%M:%S.%f'), False, categories[0], 600, 1)
        #test.delete_record(cur, 'test', 9)
        #test.delete_table(cur, 'test')
        print(data)
        #intc = False
        #for i in range(10):
        #    if categories[i - (5 * (i // 5))] == "Salary":
        #        intc = True
        #    else:
        #        intc = False
        #    await test.insert_record(cur, 'test2', datetime.datetime.utcnow(), intc, categories[i - (5 * (i // 5))], 100 * i + random.randint(0, 600))
        #    await asyncio.sleep(2)
    else:
        print("Таблица не создана. Создаем...")
        await test.create_table(cur, 'test2')
    await pool.putconn(connect)
    await pool.close()

if __name__ == "__main__":
    if sys.platform == "win32" and sys.version_info.minor >= 8:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    print(loop.get_debug())
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()