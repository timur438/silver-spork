from aiogram import types, F
from aiogram.fsm.context import FSMContext
from bot import dp
from database.db_session import get_db
from database.models import User, Bank, Card
from keyboards.admin_keyboards import role_3_admin_keyboard, role_4_admin_keyboard
from keyboards.menu_keyboards import role_3_keyboard, role_4_keyboard
from states import AdminStates
from decorators import role_required

@dp.message(F.text == "🛠️ Админ панель")
@role_required(3)
async def cmd_admin_panel(message: types.Message, state: FSMContext):
    await state.clear()
    db = next(get_db())
    user = db.query(User).filter(User.id == message.from_user.id).first()

    if user.role == 3:
        await message.answer(reply_markup=role_3_admin_keyboard)
    elif user.role == 4:
        await message.answer(reply_markup=role_4_admin_keyboard)

@dp.message(F.text == "🔙 Назад")
async def cmd_back(message: types.Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.id == message.from_user.id).first()

    if user.role == 3:
        await message.answer("Выберите команду:", reply_markup=role_3_keyboard) 
    elif user.role == 4:
        await message.answer("Выберите команду:", reply_markup=role_4_keyboard) 
    
    await state.clear()

@dp.message(F.text == "💳 Добавить кэшера")
@role_required(3)
async def cmd_add_cashier(message: types.Message, state: FSMContext):
    await message.answer("Введите имя кэшера:")
    await state.set_state(AdminStates.adding_cashier)

@dp.message(AdminStates.adding_cashier)
async def process_add_cashier(message: types.Message, state: FSMContext):
    cashier_name = message.text
    db = next(get_db())
    user = db.query(User).filter(User.full_name == cashier_name).first()
    if user:
        user.role = 2 
        db.commit()
        await message.answer(f"Кэшер {cashier_name} успешно добавлен.")
    else:
        await message.answer("Пользователь не найден. Попробуйте снова.")
    await state.clear()

@dp.message(F.text == "🗑 Удалить кэшера")
@role_required(3)
async def cmd_remove_cashier(message: types.Message, state: FSMContext):
    await message.answer("Введите имя кэшера:")
    await state.set_state(AdminStates.removing_cashier)

@dp.message(AdminStates.removing_cashier)
async def process_remove_cashier(message: types.Message, state: FSMContext):
    cashier_name = message.text
    db = next(get_db())
    user = db.query(User).filter(User.full_name == cashier_name).first()
    if user and user.role == 2:
        user.role = 1 
        db.commit()
        await message.answer(f"Кэшер {cashier_name} успешно удален.")
    else:
        await message.answer("Кэшер не найден или не является инкассатором. Попробуйте снова.")
    await state.clear()

@dp.message(F.text == "🏦 Добавить админа")
@role_required(4)
async def cmd_add_admin(message: types.Message, state: FSMContext):
    await message.answer("Введите имя админа:")
    await state.set_state(AdminStates.adding_admin)

@dp.message(AdminStates.adding_admin)
async def process_add_admin(message: types.Message, state: FSMContext):
    admin_name = message.text
    db = next(get_db())
    user = db.query(User).filter(User.full_name == admin_name).first()
    if user:
        user.role = 3  
        db.commit()
        await message.answer(f"Админ {admin_name} успешно добавлен.")
    else:
        await message.answer("Пользователь не найден. Попробуйте снова.")
    await state.clear()

@dp.message(F.text == "🗑 Удалить админа")
@role_required(4)
async def cmd_remove_admin(message: types.Message, state: FSMContext):
    await message.answer("Введите имя админа:")
    await state.set_state(AdminStates.removing_admin)

@dp.message(AdminStates.removing_admin)
async def process_remove_admin(message: types.Message, state: FSMContext):
    admin_name = message.text
    db = next(get_db())
    user = db.query(User).filter(User.full_name == admin_name).first()
    if user and user.role == 3:
        user.role = 1 
        db.commit()
        await message.answer(f"Админ {admin_name} успешно удален.")
    else:
        await message.answer("Админ не найден или не является админом. Попробуйте снова.")
    await state.clear()

@dp.message(F.text == "🔒 Сменить пароль")
@role_required(4)
async def cmd_change_pass(message: types.Message, state: FSMContext):
    await message.answer("Введите текущий пароль:")
    await state.set_state(AdminStates.changing_password)

@dp.message(AdminStates.changing_password)
async def process_change_pass(message: types.Message, state: FSMContext):
    current_password = message.text
    if current_password == "your_secret_password":  # Замените на ваш текущий пароль
        await message.answer("Введите новый пароль:")
        await state.set_state(AdminStates.new_password)
    else:
        await message.answer("Неправильный текущий пароль. Попробуйте снова.")
        await state.set_state(AdminStates.changing_password)

@dp.message(AdminStates.new_password)
async def process_new_password(message: types.Message, state: FSMContext):
    new_password = message.text
    # Здесь можно добавить логику для сохранения нового пароля
    await message.answer(f"Пароль успешно изменен.")
    await state.clear()

@dp.message(F.text == "📊 Действия пользователя")
@role_required(3)
async def cmd_user_actions(message: types.Message, state: FSMContext):
    await message.answer("Команда для просмотра действий пользователя.")
