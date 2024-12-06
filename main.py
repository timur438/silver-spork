import asyncio
import logging
from bot import bot, dp
from handlers import start, menu, admin
from database.init_db import init_db

async def main():
    init_db() 
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())