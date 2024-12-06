from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from bot import dp
from database.db_session import get_db
from database.models import User, AdminSettings
from states import AuthStates
from config_reader import config
from keyboards.menu_keyboards import role_1_keyboard, role_2_keyboard, role_3_keyboard, role_4_keyboard
from utils.password_utils import verify_password

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()
    
    if user:
        if user.role == 1:
            await message.answer("Добро пожаловать! Вы можете использовать бота.", reply_markup=role_1_keyboard)
        elif user.role == 2:
            await message.answer("Добро пожаловать! Вы можете использовать бота.", reply_markup=role_2_keyboard)
        elif user.role == 3:
            await message.answer("Добро пожаловать! Вы можете использовать бота.", reply_markup=role_3_keyboard)
        elif user.role == 4:
            await message.answer("Добро пожаловать! Вы можете использовать бота.", reply_markup=role_4_keyboard)
    else:
        await message.answer("Для доступа к боту введите пароль.")
        await state.set_state(AuthStates.waiting_for_password)

@dp.message(AuthStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    db = next(get_db())
    admin_settings = db.query(AdminSettings).first()
    
    if not admin_settings or not admin_settings.hashed_password:
        await message.answer("Настройки администратора не найдены. Обратитесь к разработчику.")
        await state.clear()
        return

    if verify_password(message.text, admin_settings.hashed_password):
        role = 1
        highest_admin_usernames = config.get_highest_admin_usernames()
        if message.from_user.username in highest_admin_usernames:
            role = 4
        
        user = User(username=message.from_user.username, full_name=message.from_user.full_name, role=role)
        db.add(user)
        db.commit()

        if role == 1:
            await message.answer(f"Пароль верный. Ваш уровень доступа: {role}.", reply_markup=role_1_keyboard)
        elif role == 2:
            await message.answer(f"Пароль верный. Ваш уровень доступа: {role}.", reply_markup=role_2_keyboard)
        elif role == 3:
            await message.answer(f"Пароль верный. Ваш уровень доступа: {role}.", reply_markup=role_3_keyboard)
        elif role == 4:
            await message.answer(f"Пароль верный. Ваш уровень доступа: {role}.", reply_markup=role_4_keyboard)
        
        await state.clear()
    else:
        await message.answer("Неправильный пароль. Доступ запрещен.")
        await state.clear()
