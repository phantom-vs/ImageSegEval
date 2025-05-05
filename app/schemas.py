"""Модуль схем данных (Pydantic models) для приложения.

Содержит модели для:
- Пользователей и их аутентификации
- Обратной связи по сегментации
- Ответов API
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """Базовая модель пользователя."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Модель для создания пользователя с валидацией пароля."""
    password: str
    password_confirm: str

    @validator('password')
    def validate_password(cls, password: str) -> str:
        """Валидация пароля.

        Args:
            password: Пароль для валидации

        Returns:
            Валидный пароль

        Raises:
            ValueError: Если пароль не соответствует требованиям
        """
        if len(password) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not any(c.isupper() for c in password):
            raise ValueError("Пароль должен содержать заглавные буквы")
        if not any(c.isdigit() for c in password):
            raise ValueError("Пароль должен содержать цифры")
        return password

    @validator('password_confirm')
    def passwords_match(cls, password_confirm: str, values: dict) -> str:
        """Проверка совпадения паролей.

        Args:
            password_confirm: Подтверждение пароля
            values: Словарь с уже валидированными значениями

        Returns:
            Подтвержденный пароль

        Raises:
            ValueError: Если пароли не совпадают
        """
        if 'password' in values and password_confirm != values['password']:
            raise ValueError("Пароли не совпадают")
        return password_confirm


class UserResponse(UserBase):
    """Модель ответа с данными пользователя."""
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        """Конфигурация модели."""
        from_attributes = True


class FeedbackRequest(BaseModel):
    """Модель запроса обратной связи."""
    is_good: bool


class SegmentationBase(BaseModel):
    """Базовая модель сегментированного изображения."""
    id: int
    user_id: int
    created_at: datetime
    is_good: Optional[bool] = None

    class Config:
        """Конфигурация модели."""
        from_attributes = True


class UserDeleteResponse(BaseModel):
    """Модель ответа на удаление пользователя."""
    message: str
    deleted_user: Optional[UserResponse] = None


class ImageDeleteResponse(BaseModel):
    """Модель ответа на удаление изображения."""
    message: str
    deleted_image: Optional[SegmentationBase] = None
