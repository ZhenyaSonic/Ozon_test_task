"""Роутер для работы с уведомлениями"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from core.database import get_db
from models.notification import NotificationStatus
from schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
)
from services.notification_service import NotificationService
from logger import logger

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать уведомление",
    description=(
        "Создает новое уведомление и запускает его отправку в фоновом режиме"
    )
)
async def create_notification(
    notification_data: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> NotificationResponse:
    """
    Создание нового уведомления

    Создает уведомление со статусом 'pending' и запускает асинхронную отправку.
    Клиент получает ответ сразу, не дожидаясь завершения отправки.

    Args:
        notification_data: Данные уведомления
        background_tasks: Фоновые задачи FastAPI
        db: Сессия базы данных

    Returns:
        Созданное уведомление со статусом 'pending'
    """
    try:
        notification = NotificationService.create_notification(
            notification_data, db
        )

        background_tasks.add_task(
            NotificationService.send_notification,
            notification.id,
            notification.type
        )

        logger.info(
            f"Notification {notification.id} created and queued for sending",
            extra={
                "notification_id": notification.id,
                "user_id": notification.user_id
            }
        )

        return NotificationResponse.model_validate(notification)

    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )


@router.get(
    "/{user_id}",
    response_model=NotificationListResponse,
    summary="Получить историю уведомлений",
    description=(
        "Возвращает список уведомлений пользователя с возможностью "
        "фильтрации по статусу"
    )
)
def get_notifications(
    user_id: int,
    status: Optional[NotificationStatus] = None,
    db: Session = Depends(get_db)
) -> NotificationListResponse:
    """
    Получение истории уведомлений пользователя

    Args:
        user_id: ID пользователя
        status: Опциональный фильтр по статусу (pending, sent, failed)
        db: Сессия базы данных

    Returns:
        Список уведомлений пользователя
    """
    try:
        notifications = NotificationService.get_user_notifications(
            user_id=user_id,
            status=status,
            db=db
        )

        notification_responses = [
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ]

        logger.info(
            f"Retrieved {len(notification_responses)} notifications "
            f"for user {user_id}",
            extra={"user_id": user_id, "status": status}
        )

        return NotificationListResponse(
            notifications=notification_responses,
            total=len(notification_responses)
        )

    except Exception as e:
        logger.error(
            f"Error retrieving notifications for user {user_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )
