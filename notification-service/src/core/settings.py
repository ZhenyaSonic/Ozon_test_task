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

    EMAIL_DELAY: float = Field(default=1.0, description="Задержка отправки email")
    TELEGRAM_DELAY: float = Field(default=0.2, description="Задержка отправки telegram")
    RETRY_MAX_ATTEMPTS: int = Field(default=3, description="Максимальное количество попыток")
    ERROR_PROBABILITY: float = Field(default=0.1, description="Вероятность ошибки отправки")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
