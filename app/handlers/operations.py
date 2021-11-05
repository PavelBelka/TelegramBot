import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from psycopg.errors import OperationalError, DataError, DatabaseError, ProgrammingError, InternalError

from preload import dp, db
from states import UpdateRecord, DeleteRecord, BalanceCalculation
from middleware.throttling import rate_limit
from app.utils import *


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

@dp.message_handler(commands=['delete'])
@rate_limit(4, 'delete')
async def delete_record(message: types.Message):
    await message.answer("Выберите единицу размерности времени (минута, час, день, неделя, месяц, год):")
    await DeleteRecord.waiting_unit_of_time.set()

@dp.message_handler(state=DeleteRecord.waiting_unit_of_time)
async def delete_record_choice_unit(message: types.Message, state: FSMContext):
    check = regexp_check_time_unit(message.text)
    if not check:
        await message.answer("Пожайлуста, проверьте корректность введенных данных.")
        return
    await state.update_data(chosen_unit=message.text.lower())
    await DeleteRecord.next()
    await message.answer("Укажите значение:")

@dp.message_handler(state=DeleteRecord.waiting_amount_of_time)
async def delete_record_choice_amount(message: types.Message, state: FSMContext):
    check = regexp_check_number(message.text)
    if not check:
        await message.answer("Неверно задано число. Попробуйте еще раз.")
        return
    unit = await state.get_data()
    try:
        connect = await db.create_connection()
        cur = db.create_cursor(connect)
        current_time = datetime.datetime.utcnow()
        past_time = regexp_search_time(unit['chosen_unit'], check, current_time)
        data = await db.select_records_date(cur, str(message.from_user.id), past_time, current_time)
        list_record = generate_output_string(data)
        await DeleteRecord.next()
        await message.answer("Выберите номер записи:\n {data}".format(data=list_record))
    except (OperationalError, DataError, DatabaseError, ProgrammingError, InternalError):
        logging.exception(f"Database write error: user_id={message.from_user.id}; record={message.text}")
        await message.answer("Упс, что-то пошло не так. Выпоните команду /cancel , а затем попробуйте снова")
    finally:
        await db.delete_connection(connect)

@dp.message_handler(state=DeleteRecord.waiting_choice_record)
async def delete_record_choice_number(message: types.Message, state: FSMContext):
    check = regexp_check_number(message.text)
    if not check:
        await message.answer("Неверно задано число. Попробуйте еще раз.")
        return
    try:
        connect = await db.create_connection()
        cur = db.create_cursor(connect)
        await db.delete_record(cur, str(message.from_user.id), int(check))
        await message.answer("Запись удалена!")
    except (OperationalError, DataError, DatabaseError, ProgrammingError, InternalError):
        logging.exception(f"Database write error: user_id={message.from_user.id}; record={message.text}")
        await message.answer("Упс, что-то пошло не так. Выпоните команду /cancel , а затем попробуйте снова")
    finally:
        await state.finish()
        await db.delete_connection(connect)

@dp.message_handler(commands=['update'])
@rate_limit(4, 'delete')
async def update_record(message: types.Message):
    await message.answer("Выберите единицу размерности времени (минута, час, день, неделя, месяц, год):")
    await UpdateRecord.waiting_unit_of_time.set()

@dp.message_handler(state=UpdateRecord.waiting_unit_of_time)
async def update_record_choice_unit(message: types.Message, state: FSMContext):
    check = regexp_check_time_unit(message.text)
    if not check:
        await message.answer("Пожайлуста, проверьте корректность введенных данных.")
        return
    await state.update_data(chosen_unit=message.text.lower())
    await UpdateRecord.next()
    await message.answer("Укажите значение:")

@dp.message_handler(state=UpdateRecord.waiting_amount_of_time)
async def update_record_choice_amount(message: types.Message, state: FSMContext):
    check = regexp_check_number(message.text)
    if not check:
        await message.answer("Неверно задано число. Попробуйте еще раз.")
        return
    unit = await state.get_data()
    try:
        connect = await db.create_connection()
        cur = db.create_cursor(connect)
        current_time = datetime.datetime.utcnow()
        past_time = regexp_search_time(unit['chosen_unit'], check, current_time)
        data = await db.select_records_date(cur, str(message.from_user.id), past_time, current_time)
        list_record = generate_output_string(data)
        await UpdateRecord.next()
        await message.answer("Выберите номер записи:\n {data}".format(data=list_record))
    except (OperationalError, DataError, DatabaseError, ProgrammingError, InternalError):
        logging.exception(f"Database write error: user_id={message.from_user.id}; record={message.text}")
        await message.answer("Упс, что-то пошло не так. Выпоните команду /cancel , а затем попробуйте снова")
    finally:
        await db.delete_connection(connect)

@dp.message_handler(state=UpdateRecord.waiting_choice_record)
async def update_record_choice_number(message: types.Message, state: FSMContext):
    check = regexp_check_number(message.text)
    if not check:
        await message.answer("Неверно задано число. Попробуйте еще раз.")
        return
    await state.update_data(chosen_number=int(check))
    await UpdateRecord.next()
    await message.answer("Теперь можете изменить запись:")

@dp.message_handler(state=UpdateRecord.waiting_new_record)
async def record(message: types.Message, state: FSMContext):
    try:
        inc, categ, clock, amo = regexp_insert_record(message.text, message.date)
    except IncorrectlySetCommandKeys:
        await message.answer("Неверная запись! Проверьте и запишите снова.")
        return
    try:
        index = await state.get_data()
        connect = await db.create_connection()
        cur = db.create_cursor(connect)
        await db.update_record(cur, str(message.from_user.id), clock, inc, categ, amo, index['chosen_number'])
        await message.answer("Изменил запись: {}".format(message.text))
    except (OperationalError, DataError, DatabaseError, ProgrammingError, InternalError):
        logging.exception(f"Database write error: user_id={message.from_user.id}; record={message.text}")
        await message.answer("Упс, что-то пошло не так при изменении записи. Попробуйте снова.")
    finally:
        await state.finish()
        await db.delete_connection(connect)

@dp.message_handler(commands=['balance'])
@rate_limit(4, 'delete')
async def balance(message: types.Message):
    await message.answer("Выберите единицу размерности времени (минута, час, день, неделя, месяц, год):")
    await BalanceCalculation.waiting_unit_of_time.set()

@dp.message_handler(state=BalanceCalculation.waiting_unit_of_time)
async def balance_choice_unit(message: types.Message, state: FSMContext):
    check = regexp_check_time_unit(message.text)
    if not check:
        await message.answer("Пожайлуста, проверьте корректность введенных данных.")
        return
    await state.update_data(chosen_unit=message.text.lower())
    await BalanceCalculation.next()
    await message.answer("Укажите значение:")

@dp.message_handler(state=BalanceCalculation.waiting_amount_of_time)
async def balance_choice_amount(message: types.Message, state: FSMContext):
    check = regexp_check_number(message.text)
    if not check:
        await message.answer("Неверно задано число. Попробуйте еще раз.")
        return
    unit = await state.get_data()
    try:
        connect = await db.create_connection()
        cur = db.create_cursor(connect)
        current_time = datetime.datetime.utcnow()
        past_time = regexp_search_time(unit['chosen_unit'], check, current_time)
        data = await db.select_records_date(cur, str(message.from_user.id), past_time, current_time)
        string_data = calculate_amount(data, current_time, int(check), unit['chosen_unit'])
        await message.answer("{data}".format(data=string_data))
    except (OperationalError, DataError, DatabaseError, ProgrammingError, InternalError):
        logging.exception(f"Database write error: user_id={message.from_user.id}; record={message.text}")
        await message.answer("Упс, что-то пошло не так. Выпоните команду /cancel , а затем попробуйте снова")
    finally:
        await state.finish()
        await db.delete_connection(connect)



