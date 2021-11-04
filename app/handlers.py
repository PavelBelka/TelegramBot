import datetime
import logging
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from app.exceptions import IncorrectlySetCommandKeys
from psycopg.errors import OperationalError, DataError, DatabaseError, ProgrammingError, InternalError
from preload import dp, db
from states.delete_record import DeleteRecord
from middleware.throttling import rate_limit
from app.regexp import regs, regexp_insert_record


@dp.message_handler(CommandStart())
@rate_limit(4, 'start')
async def send_welcome(message: types.Message):
    conect = await db.create_connection()
    cur = db.create_cursor(conect)
    verify = await db.verify_table(cur, str(message.from_user.id))
    if verify:
        await message.answer("{user}, Вы уже добавлены!".format(user=message.from_user.full_name))
    else:
        await db.create_table(cur, str(message.from_user.id))
        await message.answer(
            ("Привет, {user}!\nЯ являюсь личным финансовым ботом. Просто пиши мне свои расходы и доходы, а я буду "
             "вести финансовый учет за тебя. Если нужна помощь, напиши /help").format(user=message.from_user.full_name))
    await db.delete_connection(conect)

@dp.message_handler(CommandHelp())
@rate_limit(4, 'help')
async def send_help(message: types.Message):
    await message.answer("Список комманд для управления:\n"
                         "1. /start - начать работу,\n"
                         "2. /help - помощь")

@dp.message_handler(regexp=regs[0])
async def record(message: types.Message):
    try:
        connect = await db.create_connection()
        cur = db.create_cursor(connect)
        inc, categ, clock, amo = regexp_insert_record(message.text, message.date)
        await db.insert_record(cur, str(message.from_user.id), clock, inc, categ, amo)
        await message.answer("Внес запись: {}".format(message.text))
    except IncorrectlySetCommandKeys:
        await message.answer("Неверная запись! Проверьте и запишите снова.")
    except (OperationalError, DataError, DatabaseError, ProgrammingError, InternalError):
        logging.exception(f"Database write error: user_id={message.from_user.id}; record={message.text}")
        await message.answer("Упс, что-то пошло не так при добавлении записи...")
    finally:
        await db.delete_connection(connect)

@dp.message_handler(commands=['cancel'], state='*')
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено.")

@dp.message_handler(commands=['delete'])
@rate_limit(4, 'delete')
async def delete_record(message: types.Message):
    await message.answer("Выберите единицу размерности времени (минута, час, день, неделя, месяц, год):")
    await DeleteRecord.waiting_unit_of_time.set()

@dp.message_handler(state=DeleteRecord.waiting_unit_of_time)
async def delete_record_choice_unit(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['минута', 'час', 'день', 'неделя', 'месяц', 'год']:
        await message.answer("Пожайлуста, проверьте корректность введенных данных.")
        return
    await state.update_data(chosen_unit=message.text.lower())
    await DeleteRecord.next()
    await message.answer("Укажите значение:")

@dp.message_handler(state=DeleteRecord.waiting_amount_of_time)
async def delete_record_choice_amount(message: types.Message, state: FSMContext):
    found = re.search(r'\d+', message.text, re.M | re.I)
    if not found:
        await message.answer("Неверно задано число. Попробуйте еще раз.")
        return
    else:
        unit = await state.get_data()
        connect = await db.create_connection()
        cur = db.create_cursor(connect)
        current_time = datetime.datetime.utcnow()
        if unit['chosen_unit'] == 'минута':
            delta_t = datetime.timedelta(minutes= int(found.group()))
        elif unit['chosen_unit'] == 'час':
            delta_t = datetime.timedelta(hours= int(found.group()))
        elif unit['chosen_unit'] == 'день':
            delta_t = datetime.timedelta(days= int(found.group()))
        elif unit['chosen_unit'] == 'неделя':
            delta_t = datetime.timedelta(days= 7 * int(found.group()))
        elif unit['chosen_unit'] == 'месяц':
            delta_t = datetime.timedelta(days= 30 * int(found.group()))
        elif unit['chosen_unit'] == 'год':
            delta_t = datetime.timedelta(days= 360 * int(found.group()))
        past_time = current_time - delta_t
        data = await db.select_records_date(cur, str(message.from_user.id), past_time, current_time)
        await db.delete_connection(connect)
        await DeleteRecord.next()
        await message.answer("Выберите номер записи: {data}".format(data= data))

@dp.message_handler(state=DeleteRecord.waiting_choice_record)
async def delete_record_choice_number(message: types.Message, state: FSMContext):
    found = re.search(r'\d+', message.text, re.M | re.I)
    if not found:
        await message.answer("Неверно задано число. Попробуйте еще раз.")
        return
    else:
        connect = await db.create_connection()
        cur = db.create_cursor(connect)
        await db.delete_record(cur, str(message.from_user.id), int(found.group()))
        await message.answer("Запись удалена!")
        await state.finish()
        await db.delete_connection(connect)



