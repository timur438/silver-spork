from aiogram.fsm.state import State, StatesGroup

class CardStates(StatesGroup):
    adding_bank = State()
    adding_last_four_digits = State()
    adding_daily_limit = State()
    removing_last_four_digits = State()
