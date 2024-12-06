from aiogram.fsm.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_for_password = State()

class CardStates(StatesGroup):
    adding_bank = State()
    adding_last_four_digits = State()
    adding_daily_limit = State()
    removing_last_four_digits = State()
    removing_all_cards = State()
    withdraw_card_number = State()
    withdraw_amount = State()
    withdraw_confirm = State()

class BankStates(StatesGroup):
    adding_bank_name = State()
    removing_bank_name = State()
    checking_bank_name = State()

class AdminStates(StatesGroup):
    adding_cashier = State() 
    removing_cashier = State() 
    adding_admin = State() 
    removing_admin = State() 
    changing_password = State()
    new_password = State()
    user_actions = State()

