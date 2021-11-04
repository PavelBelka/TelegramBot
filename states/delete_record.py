from aiogram.dispatcher.filters.state import State, StatesGroup

class DeleteRecord(StatesGroup):
    waiting_unit_of_time = State()
    waiting_amount_of_time = State()
    waiting_choice_record = State()