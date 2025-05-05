"""Модуль моделей базы данных SQLAlchemy.

Содержит модели для:
- Пользователей (User)
- Сегментированных изображений (Segmentation)
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, LargeBinary, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """Модель пользователя системы.

    Attributes:
        id: Уникальный идентификатор
        username: Логин пользователя (уникальный)
        email: Электронная почта (уникальная)
        hashed_password: Хешированный пароль
        is_active: Флаг активности аккаунта
        segmentations: Связь с сегментированными изображениями пользователя
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Связь с сегментациями
    segmentations = relationship("Segmentation", back_populates="user")


class Segmentation(Base):
    """Модель сегментированного изображения.

    Attributes:
        id: Уникальный идентификатор
        user_id: ID пользователя, загрузившего изображение
        original_image: Оригинальное изображение в бинарном виде
        segmented_image: Результат сегментации в бинарном виде
        is_good: Оценка качества сегментации (None - не оценено)
        created_at: Дата и время создания записи
        user: Связь с пользователем
    """
    __tablename__ = "segmentations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    original_image = Column(LargeBinary)
    segmented_image = Column(LargeBinary)
    is_good = Column(Boolean, nullable=True)  # None - не оценено, True - хорошо, False - плохо
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # func.now - специальный SQL-конструктор

    # Связь с пользователем
    user = relationship("User", back_populates="segmentations")
