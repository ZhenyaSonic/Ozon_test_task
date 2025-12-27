from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения через переменные окружения"""

    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")
    LOG_FORMAT: str = Field(
        default="json",
        description="Формат логов (json или text)"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
