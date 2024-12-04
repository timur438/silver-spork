from aiogram import types
from aiogram.filters.command import Command
from bot import dp

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")