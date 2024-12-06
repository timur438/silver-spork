import bcrypt

def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
