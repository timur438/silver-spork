from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

role_3_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Добавить кэшера"), KeyboardButton(text="🗑 Удалить кэшера")],
        [KeyboardButton(text="📊 Действия пользователя"), KeyboardButton(text="👤 Профиль пользователя")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True,
    selective=True
)

role_4_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Добавить кэшера"), KeyboardButton(text="🗑 Удалить кэшера")],
        [KeyboardButton(text="🏦 Добавить админа"), KeyboardButton(text="🗑 Удалить админа")],
        [KeyboardButton(text="📊 Действия пользователя"), KeyboardButton(text="👤 Профиль пользователя")],
        [KeyboardButton(text="🔒 Сменить пароль")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True,
    selective=True
)