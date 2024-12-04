from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from bot import dp
from database.db_session import get_db
from database.models import User
from states import AuthStates
from config_reader import config

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()
    if user:
        await message.answer(f"Добро пожаловать! Ваш уровень доступа: {user.role}.")
    else:
        await message.answer("Для доступа к боту введите пароль.")
        await state.set_state(AuthStates.waiting_for_password)

@dp.message(AuthStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    db = next(get_db())
    if message.text == config.password:
        role = 1
        highest_admin_usernames = config.get_highest_admin_usernames()
        if message.from_user.username in highest_admin_usernames:
            role = 4
        user = User(username=message.from_user.username, full_name=message.from_user.full_name, role=role)
        db.add(user)
        db.commit()
        await message.answer(f"Пароль верный. Ваш уровень доступа: {role}.")
        await state.clear()
    else:
        await message.answer("Неправильный пароль. Доступ запрещен.")
        await state.clear()
