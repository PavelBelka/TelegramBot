from aiogram.dispatcher.filters.state import State, StatesGroup

class UpdateRecord(StatesGroup):
    waiting_unit_of_time = State()
    waiting_amount_of_time = State()
    waiting_choice_record = State()
    waiting_new_record = State()