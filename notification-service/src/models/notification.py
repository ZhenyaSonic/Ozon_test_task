"""Модель уведомления в базе данных"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from enum import Enum
from core.database import Base
from core.settings import settings


def get_default_attempts():
    """Функция для получения начального значения попыток из settings"""
    return settings.NOTIFICATION_INITIAL_ATTEMPTS


class NotificationType(str, Enum):
    """Тип уведомления"""
    EMAIL = "email"
    TELEGRAM = "telegram"


class NotificationStatus(str, Enum):
    """Статус уведомления"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base):
    """Модель уведомления"""
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(String, nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    attempts = Column(
        Integer,
        default=get_default_attempts,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, status={self.status})>"
