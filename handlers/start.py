from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from bot import dp
from database.db_session import get_db
from database.models import User
from states import AuthStates

PASSWORD = "your_secret_password"

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()
    if user:
        await message.answer("Welcome back! You can use the bot.")
    else:
        await message.answer("Please enter the password to access the bot.")
        await state.set_state(AuthStates.waiting_for_password)

@dp.message(AuthStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    db = next(get_db())
    if message.text == PASSWORD:
        user = User(username=message.from_user.username, full_name=message.from_user.full_name)
        db.add(user)
        db.commit()
        await message.answer("Password is correct. You have been granted access.")
        await state.clear()
    else:
        await message.answer("Incorrect password. Access denied.")
        await state.clear()
