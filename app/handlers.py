from aiogram import types
from preload import dp, db

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    conect = await db.create_connection()
    cur = db.create_cursor(conect)
    print(str(message.from_user.id))
    verify = await db.verify_table(cur, str(message.from_user.id))
    if verify:
        await message.answer("{user}, Вы уже добавлены!".format(user=message.from_user.full_name))
    else:
        await db.create_table(cur, str(message.from_user.id))
        await message.answer(
            ("Привет, {user}!\nЯ являюсь личным финансовым ботом. Просто пиши мне свои расходы и доходы, а я буду "
             "вести финансовый учет за тебя. Если нужна помощь, напиши /help").format(user=message.from_user.full_name))
    await db.delete_connection(conect)

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("Список комманд для управления:\n"
                         "1. /start - начать работу,\n"
                         "2. /help - помощь")