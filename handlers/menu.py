from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.filters.text import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from bot import dp
from database.db_session import get_db
from database.models import User, Bank, Card
from states.card_states import CardStates

# Создаем клавиатуры для разных ролей
role_1_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Добавить карту"), KeyboardButton(text="🗑 Удалить карту")],
        [KeyboardButton(text="🏦 Добавить банк"), KeyboardButton(text="🏦 Удалить банк")],
    ],
    resize_keyboard=True,
    selective=True
)

role_2_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💸 Съём"), KeyboardButton(text="💳 Добавить карту")],
        [KeyboardButton(text="🗑 Удалить карту"), KeyboardButton(text="🗑 Удалить все карты")],
        [KeyboardButton(text="🏦 Добавить банк"), KeyboardButton(text="🏦 Удалить банк")],
        [KeyboardButton(text="💸 Перевод")],
    ],
    resize_keyboard=True,
    selective=True
)

role_3_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💸 Съём"), KeyboardButton(text="💳 Добавить карту")],
        [KeyboardButton(text="🗑 Удалить карту"), KeyboardButton(text="🗑 Удалить все карты")],
        [KeyboardButton(text="🏦 Добавить банк"), KeyboardButton(text="🏦 Удалить банк")],
        [KeyboardButton(text="💸 Перевод"), KeyboardButton(text="🔄 Обнулить кассу")],
        [KeyboardButton(text="📊 Статистика")],
    ],
    resize_keyboard=True,
    selective=True
)

role_4_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💸 Съём"), KeyboardButton(text="💳 Добавить карту")],
        [KeyboardButton(text="🗑 Удалить карту"), KeyboardButton(text="🗑 Удалить все карты")],
        [KeyboardButton(text="🏦 Добавить банк"), KeyboardButton(text="🏦 Удалить банк")],
        [KeyboardButton(text="💸 Перевод"), KeyboardButton(text="🔄 Обнулить кассу")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🔒 Сменить пароль")],
    ],
    resize_keyboard=True,
    selective=True
)

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()
    if user:
        if user.role == 1:
            await message.answer("Выберите команду:", reply_markup=role_1_keyboard)
        elif user.role == 2:
            await message.answer("Выберите команду:", reply_markup=role_2_keyboard)
        elif user.role == 3:
            await message.answer("Выберите команду:", reply_markup=role_3_keyboard)
        elif user.role == 4:
            await message.answer("Выберите команду:", reply_markup=role_4_keyboard)

# Обработчики для текстовых команд
@dp.message(F.text == "💸 Съём")
async def cmd_withdraw(message: types.Message):
    await message.answer("Команда для снятия средств.")

@dp.message(F.text == "💳 Добавить карту")
async def cmd_add_card(message: types.Message, state: FSMContext):
    await message.answer("Введите название банка:")
    await state.set_state(CardStates.adding_bank)

@dp.message(CardStates.adding_bank)
async def process_bank(message: types.Message, state: FSMContext):
    db = next(get_db())
    bank = db.query(Bank).filter(Bank.name == message.text).first()
    if bank:
        await state.update_data(bank_id=bank.id)
        await message.answer("Введите последние 4 цифры карты:")
        await state.set_state(CardStates.adding_last_four_digits)
    else:
        await message.answer("Банк не найден. Попробуйте снова.")
        await state.set_state(CardStates.adding_bank)

@dp.message(CardStates.adding_last_four_digits)
async def process_last_four_digits(message: types.Message, state: FSMContext):
    await state.update_data(last_four_digits=message.text)
    await message.answer("Введите суточный лимит:")
    await state.set_state(CardStates.adding_daily_limit)

@dp.message(CardStates.adding_daily_limit)
async def process_daily_limit(message: types.Message, state: FSMContext):
    db = next(get_db())
    data = await state.get_data()
    bank_id = data.get('bank_id')
    last_four_digits = data.get('last_four_digits')
    daily_limit = float(message.text)

    card = Card(
        bank_id=bank_id,
        last_four_digits=last_four_digits,
        daily_limit=daily_limit,
        remaining_limit=daily_limit,
        current_balance=0.0
    )
    db.add(card)
    db.commit()
    await message.answer("Карта успешно добавлена.")
    await state.clear()

@dp.message(F.text == "🗑 Удалить карту")
async def cmd_remove_card(message: types.Message, state: FSMContext):
    await message.answer("Введите последние 4 цифры карты:")
    await state.set_state(CardStates.removing_last_four_digits)

@dp.message(CardStates.removing_last_four_digits)
async def process_remove_card(message: types.Message, state: FSMContext):
    db = next(get_db())
    card = db.query(Card).filter(Card.last_four_digits == message.text).first()
    if card:
        db.delete(card)
        db.commit()
        await message.answer("Карта успешно удалена.")
    else:
        await message.answer("Карта не найдена. Попробуйте снова.")
    await state.clear()

@dp.message(F.text == "🗑 Удалить все карты")
async def cmd_remove_all_cards(message: types.Message):
    await message.answer("Команда для удаления всех карт.")

@dp.message(F.text == "🏦 Добавить банк")
async def cmd_add_bank(message: types.Message):
    await message.answer("Введите название банка:")

@dp.message(F.text == "🏦 Удалить банк")
async def cmd_remove_bank(message: types.Message):
    await message.answer("Команда для удаления банка.")

@dp.message(F.text == "💸 Перевод")
async def cmd_transfer(message: types.Message):
    await message.answer("Команда для перевода средств.")

@dp.message(F.text == "🔄 Обнулить кассу")
async def cmd_casher_reset(message: types.Message):
    await message.answer("Команда для обнуления кассы.")

@dp.message(F.text == "📊 Статистика")
async def cmd_info(message: types.Message):
    await message.answer("Команда для отображения статистики.")

@dp.message(F.text == "🔒 Сменить пароль")
async def cmd_change_pass(message: types.Message):
    await message.answer("Команда для смены пароля.")
