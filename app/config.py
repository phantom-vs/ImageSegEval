"""Модуль конфигурации приложения.

Содержит настройки:
- Безопасности (секретные ключи, алгоритмы)
- Времени жизни токенов
- Окружения (загрузка из .env файла)
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Основные настройки приложения.

    Attributes:
        SECRET_KEY: Секретный ключ для подписи JWT токенов
        ALGORITHM: Алгоритм подписи токенов
        ACCESS_TOKEN_EXPIRE_MINUTES: Время жизни токена в минутах
    """

    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        """Конфигурация загрузки настроек.

        Attributes:
            env_file: Путь к файлу .env для загрузки переменных окружения
        """
        env_file = ".env"


settings = Settings()
