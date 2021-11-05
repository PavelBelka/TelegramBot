import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from app.exceptions import IncorrectlySetCommandKeys
from psycopg.errors import OperationalError, DataError, DatabaseError, ProgrammingError, InternalError
from preload import dp, db
from states.delete_record import DeleteRecord
from middleware.throttling import rate_limit
from app.regexp import regs, regexp_insert_record, regexp_check_number, regexp_search_time,regexp_check_time_unit, \
                       generate_output_string


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
    await message.answer(''' Помощь\n
Чтобы внести свой расход или доход нужно написать следующую фразу:\n
Расход с:600 еда 04.11.2021 22:58:00\n
Расшифровка команд приведенной выше фразы:
- Расход  - тип проведенной операции. Обязательный параметр.
Для записи о том, что вы произвели расход подходят следующие фразы: Расход, Оплата, Покупка.
Соответственно, для записи о доходе нужно написать Доход.
- c:600 - сумма вашего расхода или дохода. Обязательный параметр.
Пишется так: с:сумма_операции.
- еда - категория, в которой была произведена операция. Необязательный параметр.
Всего категорий несколько: Общее, Еда, Транспорт, Бытовые, Зарплата.
Если пропустить этот параметр, то операции автоматически присвоится категория Общее.
- 04.11.2021 - дата вашей операции. Необязательный параметр.
Если пропустить этот параметр, то будет использована дата отправки сообщения боту.
- 22:58:00 - время вашей операции. Необязательный параметр.
Следует учесть, что время записывается по UTC, а не по местному времени.
Если пропустить этот параметр, то будет использована время отправки сообщения боту.
\n
---------------------------------
\n
Список команд для управления:
1. /start - начать работу,
2. /help - помощь,
3. /cancel - отмена действия. Работает только с /delete,
4. /delete - удаление ненужной записи''')

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
    connect = await db.create_connection()
    cur = db.create_cursor(connect)
    current_time = datetime.datetime.utcnow()
    past_time = regexp_search_time(unit['chosen_unit'], check, current_time)
    data = await db.select_records_date(cur, str(message.from_user.id), past_time, current_time)
    list_record = generate_output_string(data)
    await db.delete_connection(connect)
    await DeleteRecord.next()
    await message.answer("Выберите номер записи:\n {data}".format(data= list_record))

@dp.message_handler(state=DeleteRecord.waiting_choice_record)
async def delete_record_choice_number(message: types.Message, state: FSMContext):
    check = regexp_check_number(message.text)
    if not check:
        await message.answer("Неверно задано число. Попробуйте еще раз.")
        return
    connect = await db.create_connection()
    cur = db.create_cursor(connect)
    await db.delete_record(cur, str(message.from_user.id), int(check))
    await message.answer("Запись удалена!")
    await state.finish()
    await db.delete_connection(connect)



