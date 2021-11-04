import asyncio
import datetime
import logging
import os
import re
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
                                                                 "dbname": "FinBot",
                                                                 "autocommit": "True"})
    test = Database()
    connect = await pool.getconn()
    cur = test.create_cursor(connect)
    verify = await test.verify_table(cur, 'test2')
    regs = (r'(Оплата|Покупка|Доход|Расход)', r'(?<=с:)\d+', r'(Общее|Еда|Транспорт|Бытовые|Зарплата)',
            r'(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.([0-9]{4})', r'(([01][0-9])|(2[0-3])):[0-5][0-9]:[0-5][0-9]$')
    command = list()
    if verify:
        print("Таблица уже создана")
        #text = "Оплата  с:250      02.11.2021"
        #entries = re.split(regs[0], text)
        #for reg in regs:
        #    found = re.search(reg, text, re.M|re.I)
         #   if found:
         #       command.append(found.group())
        #    else:
        #        command.append(None)
        #if command[0] is not None or command[1] is not None:
        #    if command[0].lower() == "оплата" or command[0].lower() == "расход" or command[0].lower() == "покупка":
        #        come = False
         #   elif command[0].lower() == "доход":
         #       come = True
         #   else:
         #       come = False
         #   if command[1].lower() == "общее":
         #       type_cat = categories[0]
         #   elif command[1].lower() == "еда":
         #       type_cat = categories[1]
         #   elif command[1].lower() == "транспорт":
          #      type_cat = categories[2]
        #    elif command[1].lower() == "бытовые":
        #        type_cat = categories[3]
         #   elif command[1].lower() == "зарплата":
         #       type_cat = categories[4]
         #   else:
         #       type_cat = categories[0]
         #   posix_date = 1635878220
         #   reserve_date = datetime.datetime.utcfromtimestamp(posix_date)
         #   if command[3] is not None:
         #       date = datetime.datetime.strptime(command[3], '%d.%m.%Y')
          #  else:
        #        date = datetime.datetime.combine(reserve_date.date(), datetime.time.min)
#
         #   if command[4] is not None:
         #       time_d = datetime.datetime.strptime(command[4], '%H:%M:%S')
          #  else:
          #      time_d = datetime.datetime.combine(datetime.date.min, reserve_date.time())
         #   if command[3] is None and command[4] is None:
           #     result_date = reserve_date
         #       print("reserve_date: ", result_date)
         #   else:
         #       result_date = datetime.datetime.combine(date.date(), time_d.time())
         #       print("result_date: ", result_date)
          #  await test.insert_record(cur, 'test2', result_date, come, type_cat, command[1])
          #  print("Записано")
        #else:
         #   print("Ошибка выдачи комманды")
        #print(command)
        data = await test.select_records_date(cur, '1271198784', "2021-11-04 12:40:00", "2021-11-04 17:43:00")
        print(data)
        #test.update_record(cur, 'test', datetime.datetime.strptime("2021-10-19 18:38:45.159014", '%Y-%m-%d %H:%M:%S.%f'), False, categories[0], 600, 1)
        #test.delete_record(cur, 'test', 9)
        #test.delete_table(cur, 'test')
        #print(data)
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