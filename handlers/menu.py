from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot import dp
from database.db_session import get_db
from database.models import User

role_1_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Добавить карточку"), KeyboardButton(text="🗑 Удалить карту")],
        [KeyboardButton(text="🏦 Добавить банк"), KeyboardButton(text="🏦 Удалить банк")],
    ],
    resize_keyboard=True,
    selective=True
)

role_2_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💸 Съём"), KeyboardButton(text="💳 Добавить карточку")],
        [KeyboardButton(text="🗑 Удалить карту"), KeyboardButton(text="🗑 Удалить все карты")],
        [KeyboardButton(text="🏦 Добавить банк"), KeyboardButton(text="🏦 Удалить банк")],
        [KeyboardButton(text="💸 Перевод")],
    ],
    resize_keyboard=True,
    selective=True
)

role_3_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💸 Съём"), KeyboardButton(text="💳 Добавить карточку")],
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
        [KeyboardButton(text="💸 Съём"), KeyboardButton(text="💳 Добавить карточку")],
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

@dp.message(F.text == "💸 Съём")
async def cmd_withdraw(message: types.Message):
    await message.answer("Команда для снятия средств.")

@dp.message(F.text == "💳 Добавить карточку")
async def cmd_add_card(message: types.Message):
    await message.answer("Команда для добавления карточки.")

@dp.message(F.text == "🗑 Удалить карту")
async def cmd_remove_card(message: types.Message):
    await message.answer("Команда для удаления карты.")

@dp.message(F.text == "🗑 Удалить все карты")
async def cmd_remove_all_cards(message: types.Message):
    await message.answer("Команда для удаления всех карт.")

@dp.message(F.text == "🏦 Добавить банк")
async def cmd_add_bank(message: types.Message):
    await message.answer("Команда для добавления банка.")

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
