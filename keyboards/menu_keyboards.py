from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
        [KeyboardButton(text="💸 Перевод"), KeyboardButton(text="📊 Статистика")],
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
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🛠️ Админ панель")],
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
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🛠️ Админ панель")],
    ],
    resize_keyboard=True,
    selective=True
)
