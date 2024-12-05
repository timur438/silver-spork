import re
from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from bot import dp
from database.db_session import get_db
from database.models import User, Bank, Card
from states import CardStates, BankStates
from decorators import role_required

def parse_amount(amount_str):
    amount_str = amount_str.replace(' ', '').replace('.', '').replace(',', '')
    amount = int(amount_str)
    return amount

@dp.message(F.text == "💸 Съём")
@role_required(2)
async def cmd_withdraw(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите последние 4 цифры карты:")
    await state.set_state(CardStates.withdraw_card_number)

@dp.message(CardStates.withdraw_card_number)
async def process_withdraw_card_number(message: types.Message, state: FSMContext):
    if re.match(r'^\d{4}$', message.text):
        await state.update_data(last_four_digits=message.text)
        await message.answer("Введите сумму для списания (например, 400 или 400.000):")
        await state.set_state(CardStates.withdraw_amount)
    else:
        await message.answer("Пожалуйста, введите ровно 4 цифры.")
        await state.set_state(CardStates.withdraw_card_number)

@dp.message(CardStates.withdraw_amount)
async def process_withdraw_amount(message: types.Message, state: FSMContext):
    amount = parse_amount(message.text)
    data = await state.get_data()
    last_four_digits = data.get('last_four_digits')

    db = next(get_db())
    card = db.query(Card).filter(Card.last_four_digits == last_four_digits).first()

    if card and card.remaining_limit >= amount:
        await state.update_data(amount=amount)
        await message.answer(f"Подтвердите списание {amount} с карты (да/нет):")
        await state.set_state(CardStates.withdraw_confirm)
    else:
        await message.answer("Недостаточно средств на карте или карта не найдена. Попробуйте снова.")
        await state.clear()

@dp.message(CardStates.withdraw_confirm)
async def process_withdraw_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        data = await state.get_data()
        last_four_digits = data.get('last_four_digits')
        amount = data.get('amount')

        db = next(get_db())
        card = db.query(Card).filter(Card.last_four_digits == last_four_digits).first()

        if card:
            card.remaining_limit -= amount
            db.commit()
            await message.answer(f"С карты успешно списано {amount}.")
        else:
            await message.answer("Карта не найдена. Попробуйте снова.")
        await state.clear()
    else:
        await message.answer("Списание отменено.")
        await state.clear()

@dp.message(F.text == "💳 Добавить карту")
async def cmd_add_card(message: types.Message, state: FSMContext):
    await state.clear()
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
    if re.match(r'^\d{4}$', message.text):
        await state.update_data(last_four_digits=message.text)
        await message.answer("Введите суточный лимит (например, 400000 или 400.000):")
        await state.set_state(CardStates.adding_daily_limit)
    else:
        await message.answer("Пожалуйста, введите ровно 4 цифры.")
        await state.set_state(CardStates.adding_last_four_digits)

@dp.message(CardStates.adding_daily_limit)
async def process_daily_limit(message: types.Message, state: FSMContext):
    daily_limit = parse_amount(message.text)
    db = next(get_db())
    data = await state.get_data()
    bank_id = data.get('bank_id')
    last_four_digits = data.get('last_four_digits')

    card = Card(
        bank_id=bank_id,
        last_four_digits=last_four_digits,
        daily_limit=daily_limit,
        remaining_limit=daily_limit
    )
    db.add(card)
    db.commit()
    await message.answer("Карта успешно добавлена.")
    await state.clear()

@dp.message(F.text == "🗑 Удалить карту")
async def cmd_remove_card(message: types.Message, state: FSMContext):
    await state.clear()
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
@role_required(3)
async def cmd_remove_all_cards(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Подтвердите удаление всех карт (да/нет):")
    await state.set_state(CardStates.removing_all_cards)

@dp.message(CardStates.removing_all_cards)
async def process_remove_all_cards(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        db = next(get_db())
        db.query(Card).delete()
        db.commit()
        await message.answer("Все карты успешно удалены.")
    else:
        await message.answer("Удаление всех карт отменено.")
    await state.clear()

@dp.message(F.text == "🏦 Добавить банк")
async def cmd_add_bank(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название банка:")
    await state.set_state(BankStates.checking_bank_name)

@dp.message(BankStates.checking_bank_name)
async def process_check_bank(message: types.Message, state: FSMContext):
    db = next(get_db())
    bank = db.query(Bank).filter(Bank.name == message.text).first()
    if bank:
        await message.answer("Банк с таким названием уже существует. Попробуйте снова.")
        await state.set_state(BankStates.checking_bank_name)
    else:
        bank = Bank(name=message.text)
        db.add(bank)
        db.commit()
        await message.answer("Банк успешно добавлен.")
        await state.clear()

@dp.message(F.text == "🏦 Удалить банк")
async def cmd_remove_bank(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название банка:")
    await state.set_state(BankStates.removing_bank_name)

@dp.message(BankStates.removing_bank_name)
async def process_remove_bank(message: types.Message, state: FSMContext):
    db = next(get_db())
    bank = db.query(Bank).filter(Bank.name == message.text).first()
    if bank:
        db.delete(bank)
        db.commit()
        await message.answer("Банк успешно удален.")
    else:
        await message.answer("Банк не найден. Попробуйте снова.")
    await state.clear()

@dp.message(F.text == "💸 Перевод")
@role_required(3)
async def cmd_transfer(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Команда для перевода средств.")

@dp.message(F.text == "🔄 Обнулить кассу")
@role_required(3)
async def cmd_casher_reset(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Команда для обнуления кассы.")

@dp.message(F.text == "📊 Статистика")
@role_required(2)
async def cmd_info(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Команда для отображения статистики.")

