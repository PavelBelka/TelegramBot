from aiogram import types
from main import dp

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        ("Привет, {user}!\nЯ являюсь личным финансовым ботом. Просто пиши мне свои расходы и доходы, а я буду "
         "вести финансовый учет за тебя. Если нужна помощь, напиши /help").format(user=message.from_user.full_name))