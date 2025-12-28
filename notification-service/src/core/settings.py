"""Сервис начальных настроек """
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения через переменные окружения"""
    APP_NAME: str = "Smart Notification System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Режим отладки")

    APP_HOST: str = Field(default="0.0.0.0", description="Хост приложения")
    APP_PORT: int = Field(default=8000, description="Порт приложения")

    DATABASE_URL: Optional[PostgresDsn] = Field(
        default=None,
        description="URL подключения к PostgreSQL"
    )

    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")
    LOG_FORMAT: str = Field(
        default="json",
        description="Формат логов (json или text)"
    )

    EMAIL_DELAY: float = Field(
        default=1.0, description="Задержка отправки email"
    )
    TELEGRAM_DELAY: float = Field(
        default=0.2, description="Задержка отправки telegram"
    )
    RETRY_MAX_ATTEMPTS: int = Field(
        default=3, description="Максимальное количество попыток"
    )
    ERROR_PROBABILITY: float = Field(
        default=0.1, description="Вероятность ошибки отправки"
    )

    # Форматирование времени
    TIME_FORMAT_DECIMAL_PLACES: int = Field(
        default=3, description="Количество знаков после запятой для времени"
    )
    MILLISECONDS_TO_TRIM: int = Field(
        default=3, description="Количество символов для обрезки строки миллисекунд"
    )

    # Форматы логирования
    LOG_TEXT_FORMAT: str = Field(
        default="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        description="Формат текстового лога"
    )
    LOG_DATE_FORMAT: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Формат даты в логах"
    )

    # База данных
    SQLITE_DEFAULT_PATH: str = Field(
        default="sqlite:///./notifications.db",
        description="Путь к SQLite базе данных по умолчанию"
    )
    DATABASE_CONNECT_TIMEOUT: int = Field(
        default=5,
        description="Таймаут подключения к БД в секундах"
    )
    DATABASE_HEALTH_CHECK_QUERY: str = Field(
        default="SELECT 1",
        description="SQL запрос для проверки подключения к БД"
    )

    # Уведомления
    NOTIFICATION_INITIAL_ATTEMPTS: int = Field(
        default=0,
        description="Начальное количество попыток отправки уведомления"
    )
    NOTIFICATION_RETRY_START_ATTEMPT: int = Field(
        default=1,
        description="Начальное значение для счетчика попыток"
    )

    # Сетевые адреса
    LOCALHOST_IP: str = Field(
        default="127.0.0.1",
        description="IP адрес localhost"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
