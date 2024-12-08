from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import dp
from datetime import datetime
from database.db_session import get_db
from database.models import User, Blacklist
from keyboards.admin_keyboards import role_3_admin_keyboard, role_4_admin_keyboard
from keyboards.menu_keyboards import role_3_keyboard, role_4_keyboard
from states import AdminStates
from utils.decorators import role_required
from database.models import AdminSettings
from utils.password_utils import hash_password, verify_password

def get_users_keyboard(role: int) -> InlineKeyboardMarkup:
    db = next(get_db())
    users = db.query(User).filter(User.role == role).all()

    buttons = []
    for user in users:
        buttons.append(InlineKeyboardButton(text=f"@{user.username}", callback_data=f"user_{user.username}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons], row_width=1)

    return keyboard

@dp.message(F.text == "🛠️ Админ панель")
@role_required(3)
async def cmd_admin_panel(message: types.Message, state: FSMContext):
    await state.clear()
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()

    if user.role == 3:
        await message.answer("Панель администратора", reply_markup=role_3_admin_keyboard)
    elif user.role == 4:
        await message.answer("Панель администратора", reply_markup=role_4_admin_keyboard)


@dp.message(F.text == "🔙 Назад")
async def cmd_back(message: types.Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()

    if user.role == 3:
        await message.answer("Общее меню", reply_markup=role_3_keyboard) 
    elif user.role == 4:
        await message.answer("Общее меню", reply_markup=role_4_keyboard) 
    
    await state.clear()


# Добавление кэшера
@dp.message(F.text == "💳 Добавить кэшера")
@role_required(3)
async def cmd_add_cashier(message: types.Message, state: FSMContext):
    await message.answer("Введите юзернейм кэшера, которого хотите добавить:")
    await state.set_state(AdminStates.adding_cashier)


@dp.message(AdminStates.adding_cashier)
async def process_add_cashier(message: types.Message, state: FSMContext):
    cashier_name = message.text
    db = next(get_db())
    user = db.query(User).filter(User.username == cashier_name).first()

    if user:
        if user.role >= 2: 
            await message.answer("Невозможно добавить пользователя с более высокой ролью.")
        else:
            user.role = 2 
            db.commit()
            await message.answer(f"Кэшер {cashier_name} успешно добавлен.")
    else:
        await message.answer("Пользователь не найден. Попробуйте снова.")
    await state.clear()

@dp.message(F.text == "🏦 Добавить админа")
@role_required(4)
async def cmd_add_admin(message: types.Message, state: FSMContext):
    await message.answer("Введите юзернейм админа, которого хотите добавить:")
    await state.set_state(AdminStates.adding_admin)


@dp.message(AdminStates.adding_admin)
async def process_add_admin(message: types.Message, state: FSMContext):
    admin_name = message.text
    db = next(get_db())
    user = db.query(User).filter(User.username == admin_name).first()

    if user:
        if user.role >= 3:
            await message.answer("Невозможно добавить пользователя с более высокой ролью.")
        else:
            user.role = 3
            db.commit()
            await message.answer(f"Админ {admin_name} успешно добавлен.")
    else:
        await message.answer("Пользователь не найден. Попробуйте снова.")
    await state.clear()

@dp.message(F.text == "🗑 Удалить админа")
@role_required(4)
async def cmd_remove_admin(message: types.Message, state: FSMContext):
    await message.answer("Выберите админа для удаления:", reply_markup=get_users_keyboard(3))
    await state.set_state(AdminStates.removing_admin)


@dp.callback_query(AdminStates.removing_admin)
async def process_remove_admin(callback_query: types.CallbackQuery, state: FSMContext):
    username = callback_query.data.split("_")[1]
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user and user.role == 3:
        confirmation_keyboard = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("Да", callback_data=f"confirm_remove_admin_{username}"),
            InlineKeyboardButton("Нет", callback_data="cancel")
        )
        await callback_query.message.answer(
            f"Вы уверены, что хотите удалить админа @{username}?", 
            reply_markup=confirmation_keyboard
        )
    else:
        await callback_query.message.answer("Этот пользователь не является администратором.")
    await state.set_state(AdminStates.confirm_removal)


@dp.callback_query(AdminStates.confirm_removal)
async def process_confirm_removal_admin(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data.split("_")
    action = data[0]
    username = data[1]

    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if action == "confirm_remove_admin" and user:
        user.role = 1
        db.commit()
        await callback_query.message.answer(f"Админ @{username} успешно удалён.")
    elif action == "cancel":
        await callback_query.message.answer("Удаление отменено.")
    else:
        await callback_query.message.answer("Произошла ошибка.")
    
    await state.clear()

@dp.message(F.text == "🔒 Сменить пароль")
@role_required(4)
async def cmd_change_pass(message: types.Message, state: FSMContext):
    await message.answer("Введите текущий пароль:")
    await state.set_state(AdminStates.changing_password)


@dp.message(AdminStates.changing_password)
async def process_change_pass(message: types.Message, state: FSMContext):
    db = next(get_db())
    current_password = message.text

    admin_settings = db.query(AdminSettings).first()
    if not admin_settings:
        await message.answer("Ошибка: настройки администратора не найдены.")
        return

    if verify_password(current_password, admin_settings.hashed_password):
        await message.answer("Введите новый пароль:")
        await state.set_state(AdminStates.new_password)
    else:
        await message.answer("Неправильный текущий пароль. Попробуйте снова.")
        await state.set_state(AdminStates.changing_password)


@dp.message(AdminStates.new_password)
async def process_new_password(message: types.Message, state: FSMContext):
    new_password = message.text

    db = next(get_db())
    admin_settings = db.query(AdminSettings).first()
    if admin_settings:
        admin_settings.hashed_password = hash_password(new_password)
        db.commit()
        await message.answer("Пароль успешно изменен.")
    else:
        await message.answer("Ошибка: настройки администратора не найдены.")
    
    await state.clear()

@dp.message(F.text == "👤 Профиль пользователя")
@role_required(3) 
async def cmd_user_profile(message: types.Message, state: FSMContext):
    await message.answer("Введите юзернейм пользователя для просмотра его профиля:")
    await state.set_state(AdminStates.viewing_user_profile)


@dp.message(AdminStates.viewing_user_profile)
async def process_user_profile(message: types.Message, state: FSMContext):
    username = message.text
    db = next(get_db())
    
    user = db.query(User).filter(User.username == username).first()
    
    if user:
        await message.answer(f"Профиль пользователя @{user.username}\nБаланс: {user.balance}")
    else:
        await message.answer(f"Пользователь @{username} не найден.")
    
    await state.clear()

@dp.message(F.text == "🚫 Заблокировать пользователя")
@role_required(4)  
async def cmd_block_user(message: types.Message, state: FSMContext):
    db = next(get_db())
    users = db.query(User).filter(User.role < 4).all() 
    
    if not users:
        await message.answer("Нет пользователей для блокировки.")
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    for user in users:
        keyboard.add(InlineKeyboardButton(f"@{user.username}", callback_data=f"block_user_{user.username}"))

    await message.answer("Выберите пользователя для блокировки:", reply_markup=keyboard)
    await state.set_state(AdminStates.blocking_user)

@dp.callback_query(AdminStates.blocking_user)
async def process_block_user(callback_query: types.CallbackQuery, state: FSMContext):
    username = callback_query.data.split("_")[2]  
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user:
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("Да, заблокировать", callback_data=f"confirm_block_{username}"),
            InlineKeyboardButton("Отмена", callback_data="cancel_block")
        )

        await callback_query.message.answer(
            f"Вы уверены, что хотите заблокировать пользователя @{username}?",
            reply_markup=keyboard
        )
        await state.update_data(username=username)
    else:
        await callback_query.answer("Пользователь не найден.")
        await state.clear()

@dp.callback_query(AdminStates.blocking_user)
async def process_confirm_block_user(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data.split("_")[0]
    username = callback_query.data.split("_")[2]

    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if action == "confirm" and user:
        blacklisted_user = db.query(Blacklist).filter(Blacklist.username == username).first()

        if blacklisted_user:
            await callback_query.answer("Пользователь уже заблокирован.")
            await state.clear()
            return

        db.add(Blacklist(username=username, blocked_at=int(datetime.now().timestamp())))
        db.commit()

        db.delete(user)
        db.commit()

        await callback_query.message.answer(f"Пользователь @{username} успешно заблокирован и удален из базы.")
    else:
        await callback_query.message.answer("Операция отменена.")
    
    await state.clear()

@dp.callback_query(F.data == "cancel_block")
async def cancel_block(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Операция отменена.")
    await state.clear()

@dp.message(F.text == "⚡ Обнулить баланс")
@role_required(3)
async def cmd_reset_balance(message: types.Message, state: FSMContext):
    await message.answer("Введите юзернейм пользователя, чей баланс нужно обнулить:")
    await state.set_state(AdminStates.resetting_balance)

@dp.message(AdminStates.resetting_balance)
async def process_reset_balance(message: types.Message, state: FSMContext):
    username = message.text
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user:
        admin_user = db.query(User).filter(User.username == message.from_user.username).first()
        
        if admin_user.role >= user.role:
            await message.answer("Вы не можете обнулить баланс у пользователя с такой же или более высокой ролью.")
            await state.clear()
            return

        await message.answer(
            f"Вы хотите обнулить баланс пользователя @{username}.\nВыберите действие:",
            reply_markup=get_balance_reset_keyboard()
        )

        await state.update_data(username=username)
        await state.set_state(AdminStates.confirm_reset_balance)
    else:
        await message.answer(f"Пользователь с юзернеймом @{username} не найден.")
        await state.clear()

@dp.callback_query(AdminStates.confirm_reset_balance)
async def process_confirm_reset_balance(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data
    data = await state.get_data()
    username = data.get('username')

    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if action == "reset_full":
        if user:
            user.balance = 0.0
            db.commit()
            await callback_query.message.answer(f"Баланс пользователя @{username} успешно обнулён.")
        else:
            await callback_query.message.answer(f"Пользователь с юзернеймом @{username} не найден.")
    
    elif action == "reset_partial":
        await callback_query.message.answer("Введите сумму, на которую нужно обнулить баланс (например, 100.0):")
        await state.set_state(AdminStates.resetting_partial_balance)

@dp.message(AdminStates.resetting_partial_balance)
async def process_partial_balance(message: types.Message, state: FSMContext):
    amount = message.text
    amount = amount.replace('.', '')

    if not amount.isdigit():
        await message.answer("Пожалуйста, введите корректную сумму. Например, 1000 или 20000.")
        return

    amount = int(amount) 

    if amount < 0:
        await message.answer("Сумма не может быть отрицательной. Попробуйте снова.")
        return

    data = await state.get_data()
    username = data.get('username')

    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user:
        if user.balance >= amount:
            user.balance -= amount
            db.commit()
            await message.answer(f"Баланс пользователя @{username} был уменьшен на {amount}. Новый баланс: {user.balance}.")
        else:
            await message.answer(f"У пользователя @{username} недостаточно средств для уменьшения на {amount}.")
    else:
        await message.answer(f"Пользователь с юзернеймом @{username} не найден.")
    
    await state.clear()

def get_balance_reset_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Обнулить полностью", callback_data="reset_full")],
            [InlineKeyboardButton(text="Обнулить на сумму", callback_data="reset_partial")],
        ]
    )