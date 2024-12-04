from aiogram.fsm.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_for_password = State()

class CardStates(StatesGroup):
    adding_bank = State()
    adding_last_four_digits = State()
    adding_daily_limit = State()
    removing_last_four_digits = State()

class BankStates(StatesGroup):
    adding_bank_name = State()
    removing_bank_name = State()
