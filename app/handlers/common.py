from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from preload import dp, db
from middleware.throttling import rate_limit


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

@dp.message_handler(commands=['cancel'], state='*')
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено.")

@dp.message_handler(CommandHelp())
@rate_limit(4, 'help')
async def send_help(message: types.Message):
    await message.answer(''' Помощь\n
Чтобы внести свой расход или доход нужно написать следующую команду:\n
Расход с:600 еда 04.11.2021 22:58:00\n
Расшифровка команд приведенной выше команды:
- Расход  - тип проведенной операции. Обязательный параметр.
Для записи о том, что вы произвели расход подходят следующие фразы: Расход, Оплата, Покупка.
Соответственно, для записи о доходе нужно написать Доход.
- c:600 - сумма вашего расхода или дохода. Обязательный параметр. Пишется так: с:сумма_операции.
- еда - категория, в которой была произведена операция. Необязательный параметр.
Всего категорий несколько: Прочее, Питание, Проезд, Квартплата, Медицина, Зарплата.
Если пропустить этот параметр, то операции автоматически присвоится категория Прочее.
- 04.11.2021 - дата вашей операции. Необязательный параметр.
Если пропустить этот параметр, то будет использована дата отправки сообщения боту.
- 22:58:00 - время вашей операции. Необязательный параметр.
Следует учесть, что время записывается по UTC, а не по местному времени.
Если пропустить этот параметр, то будет использована время отправки сообщения боту.
\n
---------------------------------
\n
Список команд для управления:
1. /start - начать работу
2. /help - помощь
3. /cancel - отмена действия. Работает только с командами /delete, /update
4. /delete - удаление ненужной записи
5. /update - исправление ошибочной записи''')