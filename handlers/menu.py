from aiogram import types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot import dp

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/withdraw")],
        [KeyboardButton(text="/add_card")],
        [KeyboardButton(text="/remove_card")],
        [KeyboardButton(text="/remove_all_cards")],
        [KeyboardButton(text="/add_bank")],
        [KeyboardButton(text="/transfer")],
        [KeyboardButton(text="/casher_reset")],
        [KeyboardButton(text="/info")],
        [KeyboardButton(text="/change_pass")],
    ],
    resize_keyboard=True
)

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer("Выберите команду:", reply_markup=menu_keyboard)

@dp.message(Command("withdraw"))
async def cmd_withdraw(message: types.Message):
    await message.answer("Команда для снятия средств.")

@dp.message(Command("add_card"))
async def cmd_add_card(message: types.Message):
    await message.answer("Команда для добавления карточки.")

@dp.message(Command("remove_card"))
async def cmd_remove_card(message: types.Message):
    await message.answer("Команда для удаления карты.")

@dp.message(Command("remove_all_cards"))
async def cmd_remove_all_cards(message: types.Message):
    await message.answer("Команда для удаления всех карт.")

@dp.message(Command("add_bank"))
async def cmd_add_bank(message: types.Message):
    await message.answer("Команда для добавления банка.")

@dp.message(Command("transfer"))
async def cmd_transfer(message: types.Message):
    await message.answer("Команда для перевода средств.")

@dp.message(Command("casher_reset"))
async def cmd_casher_reset(message: types.Message):
    await message.answer("Команда для обнуления кассы.")

@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    await message.answer("Команда для отображения статистики.")

@dp.message(Command("change_pass"))
async def cmd_change_pass(message: types.Message):
    await message.answer("Команда для смены пароля.")
