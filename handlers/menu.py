import re
from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from bot import dp, bot
from database.db_session import get_db
from database.models import User, Bank, Card
from states import CardStates, BankStates
from keyboards.menu_keyboards import role_1_keyboard, role_2_keyboard, role_3_keyboard, role_4_keyboard
from utils.decorators import role_required

def parse_amount(amount_str):
    amount_str = amount_str.replace(' ', '').replace('.', '').replace(',', '')
    amount = int(amount_str)
    return amount

@dp.message(F.text == "💸 Съём")
@role_required(2)
async def cmd_withdraw(message: types.Message, state: FSMContext):
    await state.clear()
    db = next(get_db())
    cards = db.query(Card).all()
    if not cards:
        await message.answer("У вас нет добавленных карт.")
        return

    card_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{card.last_four_digits} ({card.bank_name})", callback_data=f"card_{card.last_four_digits}")]
            for card in cards
        ]
    )
    await message.answer("Выберите карту для списания:", reply_markup=card_keyboard)
    await state.set_state(CardStates.withdraw_card_number)

@dp.callback_query(F.data.startswith("card_"))
async def process_withdraw_card_number_callback(callback: types.CallbackQuery, state: FSMContext):
    last_four_digits = callback.data.split("_")[1]
    await state.update_data(last_four_digits=last_four_digits)
    await callback.message.edit_text("Введите сумму для списания (например, 400 или 400.000):")
    await state.set_state(CardStates.withdraw_amount)

@dp.message(CardStates.withdraw_amount)
async def process_withdraw_amount(message: types.Message, state: FSMContext):
    amount = parse_amount(message.text)
    data = await state.get_data()
    last_four_digits = data.get('last_four_digits')

    db = next(get_db())
    card = db.query(Card).filter(Card.last_four_digits == last_four_digits).first()
    

    if card and card.remaining_limit >= amount:
        await state.update_data(amount=amount)
        confirm_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Да", callback_data="confirm_yes"), InlineKeyboardButton(text="Нет", callback_data="confirm_no")]
            ]
        )
        await message.answer(f"Подтвердите списание {amount} с карты:", reply_markup=confirm_keyboard)
        await state.set_state(CardStates.withdraw_confirm)
    else:
        await message.answer("Превышен лимит на карте или карта не найдена. Попробуйте снова.")
        await state.clear()

@dp.callback_query(F.data.startswith("confirm_"))
async def process_withdraw_confirm_callback(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "yes":
        data = await state.get_data()
        last_four_digits = data.get('last_four_digits')
        amount = data.get('amount')

        db = next(get_db())
        card = db.query(Card).filter(Card.last_four_digits == last_four_digits).first()
        user = db.query(User).filter(User.username == callback.from_user.username).first()

        if card:
            card.remaining_limit -= amount
            user.balance += amount
            db.commit()
            await callback.message.edit_text(f"С карты успешно списано {amount}.")

            channel_id = -1002436565133
            text = (
                f"Юзер @{callback.from_user.username} снял {amount:,} с карты {card.bank_name} | {card.last_four_digits}\n"
                f"Оставшийся лимит карты: {card.remaining_limit:,}\n"
                f"Текущий баланс юзера: {user.balance:,}"
            )
            await bot.send_message(chat_id=channel_id, text=text)
        else:
            await callback.message.edit_text("Карта не найдена. Попробуйте снова.")
        await state.clear()
    else:
        await callback.message.edit_text("Списание отменено.")
        await state.clear()

@dp.message(F.text == "💳 Добавить карту")
@role_required(1)
async def cmd_add_card(message: types.Message, state: FSMContext):
    await state.clear()
    db = next(get_db())
    banks = db.query(Bank).all()
    if not banks:
        await message.answer("Сначала добавьте хотя бы один банк.")
        return

    bank_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=bank.name, callback_data = f"select_bank|{bank.name}")]
            for bank in banks
        ]
    )
    await message.answer("Выберите банк:", reply_markup=bank_keyboard)

@dp.callback_query(lambda c: c.data.split("|")[0] == "select_bank")
async def process_select_bank_callback(callback: types.CallbackQuery, state: FSMContext):
    action, bank_name = callback.data.split("|")
    db = next(get_db())
    bank = db.query(Bank).filter(Bank.name == bank_name).first()
    if bank:
        await state.update_data(bank_id=bank.id, bank_name=bank.name)
        await callback.message.edit_text("Введите последние 4 цифры карты:")
        await state.set_state(CardStates.adding_last_four_digits)
    else:
        await callback.message.edit_text("Банк не найден. Попробуйте снова.")
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
    bank_name = data.get('bank_name')

    card = Card(
        bank_id=bank_id,
        last_four_digits=last_four_digits,
        daily_limit=daily_limit,
        remaining_limit=daily_limit,
        added_by=message.from_user.username,
        bank_name=bank_name
    )
    db.add(card)
    db.commit()
    await message.answer("Карта успешно добавлена.")
    await state.clear()

@dp.message(F.text == "🗑 Удалить карту")
@role_required(1)
async def cmd_remove_card(message: types.Message, state: FSMContext):
    await state.clear()
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()

    if user.role > 1:
        cards = db.query(Card).all()
    else:
        cards = db.query(Card).filter(Card.added_by == message.from_user.username).all()

    if not cards:
        await message.answer("У вас нет добавленных карт.")
        return

    card_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{card.last_four_digits} ({card.bank_name})", callback_data=f"delete_card_{card.last_four_digits}")]
            for card in cards
        ]
    )
    await message.answer("Выберите карту для удаления:", reply_markup=card_keyboard)

@dp.callback_query(F.data.startswith("delete_card_"))
async def process_remove_card_callback(callback: types.CallbackQuery, state: FSMContext):
    last_four_digits = callback.data.split("_")[2]
    db = next(get_db())
    card = db.query(Card).filter(Card.last_four_digits == last_four_digits).first()
    user = db.query(User).filter(User.username == callback.from_user.username).first()
    if card:
        if callback.from_user.username == card.added_by or user.role >= 2:
            db.delete(card)
            db.commit()
            await callback.message.edit_text("Карта успешно удалена.")
        else:
            await callback.message.edit_text("У вас нет прав для удаления этой карты.")
    else:
        await callback.message.edit_text("Карта не найдена. Попробуйте снова.")

@dp.message(F.text == "🗑 Удалить все карты")
@role_required(3)
async def cmd_remove_all_cards(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Подтвердите удаление всех карт (да/нет):", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет")]
    ))
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
@role_required(1)
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
        bank = Bank(name=message.text, added_by=message.from_user.username)
        db.add(bank)
        db.commit()
        await message.answer("Банк успешно добавлен.")
        await state.clear()

@dp.message(F.text == "🏦 Удалить банк")
@role_required(1)
async def cmd_remove_bank(message: types.Message, state: FSMContext):
    await state.clear()
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()

    if user.role > 1:
        banks = db.query(Bank).all()
    else:
        banks = db.query(Bank).filter(Bank.added_by == message.from_user.username).all()
    
    if not banks:
        await message.answer("У вас нет добавленных банков.")
        return

    bank_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=bank.name, callback_data = f"delete_bank|{bank.name}")]
            for bank in banks
        ]
    )
    await message.answer("Выберите банк для удаления:", reply_markup=bank_keyboard)

@dp.callback_query(lambda c: c.data.split("|")[0] == "delete_bank")
async def process_remove_bank_callback(callback: types.CallbackQuery, state: FSMContext):
    action, bank_name = callback.data.split("|")
    db = next(get_db())
    bank = db.query(Bank).filter(Bank.name == bank_name).first()
    user = db.query(User).filter(User.username == callback.from_user.username).first()

    if bank:
        if callback.from_user.username == bank.added_by or user.role >= 2:
            db.delete(bank)
            db.commit()
            await callback.message.edit_text("Банк успешно удален.")
        else:
            await callback.message.edit_text("У вас нет прав для удаления этого банка.")
    else:
        await callback.message.edit_text("Банк не найден. Попробуйте снова.")

@dp.message(F.text == "💸 Перевод")
@role_required(3)
async def cmd_transfer(message: types.Message, state: FSMContext):
    await state.clear()
    db = next(get_db())
    users = db.query(User).filter(User.role > 1).all()
    if not users:
        await message.answer("Нет доступных пользователей для перевода средств.")
        return

    user_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=user.username, callback_data = f"transfer_from|{user.username}")]
            for user in users
        ]
    )
    await message.answer("Выберите пользователя, с чьего баланса будут списаны средства:", reply_markup=user_keyboard)
    await state.set_state("transfer_select_from")

@dp.callback_query(lambda c: c.data.split("|")[0] == "transfer_from")
async def process_transfer_from(callback: types.CallbackQuery, state: FSMContext):
    action, username_from = callback.data.split("|")
    await state.update_data(username_from=username_from)

    db = next(get_db())
    users = db.query(User).filter(User.role > 1, User.username != username_from).all()
    user_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=user.username, callback_data = f"transfer_to|{user.username}")]
            for user in users
        ]
    )
    await callback.message.edit_text("Выберите пользователя, на чей баланс будут зачислены средства:", reply_markup=user_keyboard)
    await state.set_state("transfer_select_to")

@dp.callback_query(lambda c: c.data.split("|")[0] == "transfer_to")
async def process_transfer_to(callback: types.CallbackQuery, state: FSMContext):
    daction, username_to = callback.data.split("|")
    await state.update_data(username_to=username_to)
    await callback.message.edit_text("Введите сумму перевода (например, 400 или 400.000):")
    await state.set_state("transfer_amount")

@dp.message(F.state == "transfer_amount")
async def process_transfer_amount(message: types.Message, state: FSMContext):
    try:
        amount = parse_amount(message.text)
        data = await state.get_data()
        username_from = data.get('username_from')
        username_to = data.get('username_to')

        db = next(get_db())
        user_from = db.query(User).filter(User.username == username_from).first()
        user_to = db.query(User).filter(User.username == username_to).first()

        if user_from and user_to and user_from.role > 1 and user_to.role > 1:
            if user_from.balance >= amount:
                user_from.balance -= amount
                user_to.balance += amount
                db.commit()
                await message.answer(f"Перевод {amount} успешно выполнен с {username_from} на {username_to}.")
            else:
                await message.answer(f"Недостаточно средств на балансе {username_from}.")
        else:
            await message.answer("Перевод невозможен. Проверьте пользователей или их роли.")
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму.")

@dp.message(F.text == "📊 Статистика")
@role_required(1)
async def cmd_statistics(message: types.Message, state: FSMContext):
    await state.clear()
    db = next(get_db())
    cards = db.query(Card).all()

    if not cards:
        await message.answer("У вас нет добавленных карт.")
        return

    header = (
        "Карта  | Банк     | Лимит     | Остаток   \n"
        "-------|----------|-----------|-----------"
    )

    def format_number(number):
        return f"{int(number):,}".replace(',', ' ')

    rows = [
        f"{card.last_four_digits:<7}| {card.bank_name[:7]:<9}| {format_number(card.daily_limit):>9} | {format_number(card.remaining_limit):>10}"
        for card in cards
    ]

    table = header + "\n" + "\n".join(rows)

    await message.answer(f"📊 Ваша статистика:\n\n```\n{table}\n```", parse_mode="Markdown")

@dp.message(F.text == "👤 Мой профиль") 
@role_required(1)
async def cmd_my_profile(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.username == message.from_user.username).first()

    if user:
        profile_info = (
            f"👤 **Профиль:**\n"
            f"📌 **ID:** {user.id}\n"
            f"📛 **Юзернейм:** @{user.username}\n"
            f"📝 **Полное имя:** {user.full_name if user.full_name else 'Не указано'}\n"
            f"🔑 **Роль:** {user.role} ({get_role_name(user.role)})\n"
            f"💰 **Баланс:** {user.balance:.2f} 💵"
        )
        await message.answer(profile_info, parse_mode="HTML")
    else:
        await message.answer("Ошибка: Ваш профиль не найден в базе данных.")

def get_role_name(role_id):
    roles = {
        1: "Пользователь",
        2: "Кэшер",
        3: "Администратор",
        4: "Суперадмин",
    }
    return roles.get(role_id, "Неизвестная роль")

