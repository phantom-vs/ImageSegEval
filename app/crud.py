"""Модуль для операций с базой данных (CRUD).

Содержит функции для:
- работы с пользователями
- хеширования паролей
- проверки учетных данных
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(database_session: Session, username: str):
    """Получение пользователя по username.

    Args:
        database_session: Сессия подключения к БД
        username: Имя пользователя для поиска

    Returns:
        models.User: Найденный пользователь или None
    """
    return database_session.query(models.User).filter(
        models.User.username == username
    ).first()


def get_user_by_email(database_session: Session, email: str):
    """Получение пользователя по email.

    Args:
        database_session: Сессия подключения к БД
        email: Email пользователя для поиска

    Returns:
        models.User: Найденный пользователь или None
    """
    return database_session.query(models.User).filter(
        models.User.email == email
    ).first()


def create_user(database_session: Session, user: schemas.UserCreate):
    """Создание нового пользователя.

    Args:
        database_session: Сессия подключения к БД
        user: Данные для создания пользователя

    Returns:
        models.User: Созданный пользователь
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    database_session.add(db_user)
    database_session.commit()
    database_session.refresh(db_user)
    return db_user


def verify_password(plain_password: str, hashed_password: str):
    """Проверка соответствия пароля и его хеша.

    Args:
        plain_password: Пароль в чистом виде
        hashed_password: Хеш пароля из БД

    Returns:
        bool: Результат проверки
    """
    return pwd_context.verify(plain_password, hashed_password)
