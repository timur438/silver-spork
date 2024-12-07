import asyncio
import logging
from bot import bot, dp
from handlers import start, menu, admin
from database.init_db import init_db
from database.db_session import get_db
from database.models import AdminSettings
from utils.password_utils import hash_password
from utils.config_reader import config

def initialize_admin_password():
    db = next(get_db())
    admin_settings = db.query(AdminSettings).first()
    if not admin_settings:
        hashed_password = hash_password(config.password)
        admin_settings = AdminSettings(hashed_password=hashed_password)
        db.add(admin_settings)
        db.commit()

async def main():
    init_db() 
    initialize_admin_password()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())