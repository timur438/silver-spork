from functools import wraps
from aiogram import types
from database.db_session import get_db
from database.models import User

def role_required(role):
    def decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, *args, **kwargs):
            db = next(get_db())
            user = db.query(User).filter(User.username == message.from_user.username).first()
            if user and user.role >= role:
                return await func(message, *args, **kwargs)
            else:
                pass
        return wrapped
    return decorator
