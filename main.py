import asyncio
import logging
from bot import bot, dp
from handlers import start

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())