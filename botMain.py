import logging, psycopg2
from aiogram import Bot, Dispatcher, executor, types

class TelegramBot:
    def __init__(self, dispatcher, bot):
        self.bot = bot
        self.dp = dispatcher

    def message_register(self):
        dp.register_message_handler(self.send_welcome, commands="start")

    @staticmethod
    async def send_welcome(message: types.Message):
        await message.reply(
            ("Привет, {user}!\nЯ являюсь личным финансовым ботом. Просто пиши мне свои расходы и доходы, а я буду "
             "вести финансовый учет за тебя. Если нужна помощь, напиши /help").format(user=message.from_user.full_name))


class Connect:
    pass

#if __name__ == "__main__":
#    logging.basicConfig(level=logging.INFO)
#    conn = psycopg2.connect(dbname='FinBot', user='telefinbot', password='Yakov2020', host='localhost')
#    new_bot = Bot(token="2008283464:AAFvmqKxp6XJQhGD7cKx2VE55FBKo6qV628")
#   dp = Dispatcher(new_bot)
#    telegram = TelegramBot(dp, new_bot)
#    telegram.message_register()
#    executor.start_polling(dp, skip_updates=True)