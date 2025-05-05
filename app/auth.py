"""Модуль аутентификации и авторизации для FastAPI приложения.

Содержит функции для:
- управления сессиями БД
- аутентификации пользователей
- генерации JWT-токенов
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from . import crud
from .database import SessionLocal
from .config import settings

# Схема OAuth2 для работы с токенами
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def authenticate_user(db_session: Session, username: str, password: str):
    """Аутентификация пользователя по логину и паролю.

    Args:
        db_session: Сессия базы данных
        username: Логин пользователя
        password: Пароль для проверки

    Returns:
        User: Объект пользователя при успехе
        False: При неудачной аутентификации
    """
    user = crud.get_user(db_session, username)
    if not user or not crud.verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена доступа.

    Args:
        data: Данные для включения в токен
        expires_delta: Время жизни токена

    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
