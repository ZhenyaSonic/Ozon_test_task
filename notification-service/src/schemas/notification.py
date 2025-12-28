"""Pydantic схемы для уведомлений"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from models.notification import NotificationType, NotificationStatus
from core.constants import (
    TEST_USER_ID,
    TEST_MESSAGE_CODE,
    TEST_NOTIFICATION_ID,
    TEST_MIN_NOTIFICATIONS_COUNT
)
from core.settings import settings


class NotificationCreate(BaseModel):
    """Схема для создания уведомления"""
    user_id: int = Field(..., description="ID пользователя", example=TEST_USER_ID)
    message: str = Field(..., description="Текст сообщения", example=f"Ваш код: {TEST_MESSAGE_CODE}")
    type: NotificationType = Field(
        ...,
        description="Тип уведомления (email или telegram)",
        example="telegram"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": TEST_USER_ID,
                "message": f"Ваш код: {TEST_MESSAGE_CODE}",
                "type": "telegram"
            }
        }


class NotificationResponse(BaseModel):
    """Схема ответа с информацией об уведомлении"""
    id: int = Field(..., description="ID уведомления")
    user_id: int = Field(..., description="ID пользователя")
    message: str = Field(..., description="Текст сообщения")
    type: NotificationType = Field(..., description="Тип уведомления")
    status: NotificationStatus = Field(..., description="Статус уведомления")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время последнего обновления")
    attempts: int = Field(..., description="Количество попыток отправки")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": TEST_NOTIFICATION_ID,
                "user_id": TEST_USER_ID,
                "message": f"Ваш код: {TEST_MESSAGE_CODE}",
                "type": "telegram",
                "status": "pending",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
                "attempts": settings.NOTIFICATION_INITIAL_ATTEMPTS
            }
        }


class NotificationListResponse(BaseModel):
    """Схема ответа со списком уведомлений"""
    notifications: List[NotificationResponse] = Field(..., description="Список уведомлений")
    total: int = Field(..., description="Общее количество уведомлений")

    class Config:
        json_schema_extra = {
            "example": {
                "notifications": [
                    {
                        "id": TEST_NOTIFICATION_ID,
                        "user_id": TEST_USER_ID,
                        "message": f"Ваш код: {TEST_MESSAGE_CODE}",
                        "type": "telegram",
                        "status": "sent",
                        "created_at": "2024-01-01T12:00:00",
                        "updated_at": "2024-01-01T12:00:01",
                        "attempts": TEST_MIN_NOTIFICATIONS_COUNT
                    }
                ],
                "total": TEST_MIN_NOTIFICATIONS_COUNT
            }
        }
