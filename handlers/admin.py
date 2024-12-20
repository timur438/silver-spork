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
    """
    Генерирует инлайн-клавиатуру с пользователями, чья роль равна или меньше указанной.
    """
    db = next(get_db())
    users = db.query(User).filter(User.role <= role).all()
    keyboard = [
        [InlineKeyboardButton(text=f"@{user.username}", callback_data=f"username|{user.username}")]
        for user in users
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def format_balance(balance):
    return f"{balance:,.0f}".replace(",", " ")

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

@dp.message(F.text == "💳 Добавить кэшера")
@role_required(3)
async def cmd_add_cashier(message: types.Message, state: FSMContext):
    await message.answer("Выберите пользователя, которого хотите назначить кэшером:", reply_markup=get_users_keyboard(1))
    await state.set_state(AdminStates.adding_cashier)


@dp.callback_query(AdminStates.adding_cashier)
async def process_add_cashier_callback(callback_query: types.CallbackQuery, state: FSMContext):
    action, username = callback_query.data.split("|")
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user:
        if user.role >= 2:
            await callback_query.message.answer("Невозможно добавить пользователя с более высокой ролью.")
        else:
            user.role = 2
            db.commit()
            await callback_query.message.answer(f"Кэшер @{username} успешно добавлен.")
    else:
        await callback_query.message.answer("Пользователь не найден.")
    await state.clear()


@dp.message(F.text == "🏦 Добавить админа")
@role_required(4)
async def cmd_add_admin(message: types.Message, state: FSMContext):
    await message.answer("Выберите пользователя, которого хотите назначить админом:", reply_markup=get_users_keyboard(2))
    await state.set_state(AdminStates.adding_admin)


@dp.callback_query(AdminStates.adding_admin)
async def process_add_admin_callback(callback_query: types.CallbackQuery, state: FSMContext):
    action, username = callback_query.data.split("|")
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user:
        if user.role >= 3:
            await callback_query.message.answer("Невозможно добавить пользователя с более высокой ролью.")
        else:
            user.role = 3
            db.commit()
            await callback_query.message.answer(f"Админ @{username} успешно добавлен.")
    else:
        await callback_query.message.answer("Пользователь не найден.")
    await state.clear()


@dp.message(F.text == "🗑 Удалить админа")
@role_required(4)
async def cmd_remove_admin(message: types.Message, state: FSMContext):
    await message.answer("Выберите админа для удаления:", reply_markup=get_users_keyboard(3))
    await state.set_state(AdminStates.removing_admin)


@dp.callback_query(AdminStates.removing_admin)
async def process_remove_admin_callback(callback_query: types.CallbackQuery, state: FSMContext):
    action, username = callback_query.data.split("|")
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user and user.role == 3:
        confirmation_keyboard = InlineKeyboardMarkup(row_width=2)
        confirmation_keyboard.add(
            InlineKeyboardButton(text="Да", callback_data=f"confirm_remove_admin|{username}"),
            InlineKeyboardButton(text="Нет", callback_data="cancel")
        )
        await callback_query.message.answer(
            f"Вы уверены, что хотите удалить админа @{username}?", 
            reply_markup=confirmation_keyboard
        )
    else:
        await callback_query.message.answer("Этот пользователь не является администратором.")
    await state.clear()


@dp.callback_query(AdminStates.confirm_removal)
async def process_confirm_removal_admin(callback_query: types.CallbackQuery, state: FSMContext):
    action, username = callback_query.data.split("|")

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

def get_view_users_keyboard(role: int) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру с пользователями, чья роль равна или меньше указанной.
    """
    db = next(get_db())
    users = db.query(User).filter(User.role <= role).all()
    keyboard = [
        [InlineKeyboardButton(text=f"@{user.username}", callback_data = f"view_user|{user.username}")]
        for user in users
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(F.text == "👤 Профиль пользователя")
@role_required(3)
async def cmd_user_profile(message: types.Message, state: FSMContext):
    await message.answer(
        "Выберите пользователя для просмотра профиля или введите юзернейм:",
        reply_markup=get_view_users_keyboard(4)
    )
    await state.set_state(AdminStates.viewing_user_profile)

@dp.callback_query(lambda c: c.data.split("|")[0] == "view_user")
async def process_user_profile_callback(callback_query: types.CallbackQuery, state: FSMContext):
    action, username = callback_query.data.split("|")

    db = next(get_db())
    
    user = db.query(User).filter(User.username == username).first()
    
    if user:
        roles = {
            1: "Пользователь",
            2: "Кэшер",
            3: "Администратор",
            4: "Суперадминистратор"
        }
        role_name = roles.get(user.role, "Неизвестная роль")
        
        await callback_query.message.answer(
            f"👤 Профиль пользователя: @{user.username}\n"
            f"💰 Баланс: {format_balance(user.balance)}\n"
            f"🔑 Роль: {role_name}"
        )
    else:
        await callback_query.message.answer("Пользователь не найден.")
    
    await callback_query.answer()

@dp.message(AdminStates.viewing_user_profile)
async def process_user_profile(message: types.Message, state: FSMContext):
    username = message.text.lstrip("@")
    db = next(get_db())
    
    user = db.query(User).filter(User.username == username).first()
    
    if user:
        balance = " ".join(reversed([str(user.balance)[::-1][i:i+3] for i in range(0, len(str(user.balance)), 3)]))[::-1]
        
        roles = {
            1: "Пользователь",
            2: "Кэшер",
            3: "Администратор",
            4: "Суперадминистратор"
        }
        role_name = roles.get(user.role, "Неизвестная роль")
        
        await message.answer(
            f"👤 Профиль пользователя: @{user.username}\n"
            f"💰 Баланс: {balance}\n"
            f"🔑 Роль: {role_name}"
        )
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
        keyboard.add(InlineKeyboardButton(f"@{user.username}", callback_data=f"block_user|{user.username}"))

    await message.answer("Выберите пользователя для блокировки:", reply_markup=keyboard)
    await state.set_state(AdminStates.blocking_user)

@dp.callback_query(AdminStates.blocking_user)
async def process_block_user(callback_query: types.CallbackQuery, state: FSMContext):
    action, username = callback_query.data.split("|")
 
    if action == "block_user":
        db = next(get_db())
        user = db.query(User).filter(User.username == username).first()
    else:
        return
    
    if user:
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("Да, заблокировать", callback_data = f"confirm_block|{username}"),
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
    action, username = callback_query.data.split("|")

    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if action == "confirm_block" and user:
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
    db = next(get_db())
    admin_user = db.query(User).filter(User.username == message.from_user.username).first()

    if not admin_user:
        await message.answer("Произошла ошибка: ваш аккаунт не найден в базе данных.")
        return

    eligible_users = db.query(User).filter(User.role <= (admin_user.role - 1)).all()

    if not eligible_users:
        await message.answer("Нет пользователей с доступной для вас ролью для обнуления баланса.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"@{user.username} (Баланс: {format_balance(user.balance)})", 
                callback_data=f"select_user_{user.id}"
            )]
            for user in eligible_users
        ]
    )

    await message.answer("Выберите пользователя, чей баланс нужно обнулить:", reply_markup=keyboard)
    await state.set_state(AdminStates.selecting_user)

@dp.callback_query(AdminStates.selecting_user)
async def process_select_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.data.replace("select_user_", "")

    if not user_id.isdigit():
        await callback_query.message.answer("Некорректный выбор пользователя.")
        return

    db = next(get_db())
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        await callback_query.message.answer("Пользователь не найден.")
        await state.clear()
        return

    await callback_query.message.answer(
        f"Вы хотите обнулить баланс пользователя @{user.username} (Текущий баланс: {user.balance}).\nВыберите действие:",
        reply_markup=get_balance_reset_keyboard()
    )
    await state.update_data(user_id=user.id, username=user.username)
    await state.set_state(AdminStates.confirm_reset_balance)

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