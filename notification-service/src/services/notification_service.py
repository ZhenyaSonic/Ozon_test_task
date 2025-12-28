"""Сервис для работы с уведомлениями"""
import asyncio
import random
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.notification import (
    Notification,
    NotificationType,
    NotificationStatus
)
from schemas.notification import NotificationCreate
from core.settings import settings
from core.database import db_manager
from logger import logger


class NotificationService:
    """Сервис для управления уведомлениями"""

    @staticmethod
    async def send_notification(
        notification_id: int,
        notification_type: NotificationType
    ) -> None:
        """
        Асинхронная отправка уведомления с retry механизмом

        Args:
            notification_id: ID уведомления
            notification_type: Тип уведомления (email или telegram)
        """
        max_attempts = settings.RETRY_MAX_ATTEMPTS
        error_probability = settings.ERROR_PROBABILITY

        if notification_type == NotificationType.EMAIL:
            delay = settings.EMAIL_DELAY
        else:
            delay = settings.TELEGRAM_DELAY

        for attempt in range(settings.NOTIFICATION_RETRY_START_ATTEMPT, max_attempts + 1):
            try:
                await asyncio.sleep(delay)

                should_fail = (
                    random.random() < error_probability and attempt < max_attempts
                )
                if should_fail:
                    logger.warning(
                        f"Notification {notification_id} failed on attempt "
                        f"{attempt}, retrying..."
                    )
                    with db_manager.get_session() as session:
                        notification = session.get(Notification, notification_id)
                        if notification:
                            notification.attempts = attempt
                            session.commit()
                    continue

                with db_manager.get_session() as session:
                    notification = session.get(Notification, notification_id)
                    if notification:
                        notification.status = NotificationStatus.SENT
                        notification.attempts = attempt
                        session.commit()
                        logger.info(
                            f"Notification {notification_id} sent successfully"
                            f"after {attempt} attempt(s)"
                        )
                return

            except Exception as e:
                logger.error(
                    f"Error sending notification {notification_id} on attempt "
                    f"{attempt}: {e}"
                )
                if attempt == max_attempts:
                    with db_manager.get_session() as session:
                        notification = session.get(Notification, notification_id)
                        if notification:
                            notification.status = NotificationStatus.FAILED
                            notification.attempts = attempt
                            session.commit()
                            logger.error(
                                f"Notification {notification_id} failed after "
                                f"{max_attempts} attempts"
                            )

    @staticmethod
    def create_notification(
        notification_data: NotificationCreate,
        db: Session
    ) -> Notification:
        """
        Создание нового уведомления

        Args:
            notification_data: Данные для создания уведомления
            db: Сессия базы данных

        Returns:
            Созданное уведомление
        """
        notification = Notification(
            user_id=notification_data.user_id,
            message=notification_data.message,
            type=notification_data.type,
            status=NotificationStatus.PENDING,
            attempts=settings.NOTIFICATION_INITIAL_ATTEMPTS
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        logger.info(
            f"Created notification {notification.id} for user"
            f"{notification.user_id}"
        )
        return notification

    @staticmethod
    def get_user_notifications(
        user_id: int,
        status: Optional[NotificationStatus] = None,
        db: Session = None
    ) -> List[Notification]:
        """
        Получение списка уведомлений пользователя

        Args:
            user_id: ID пользователя
            status: Опциональный фильтр по статусу
            db: Сессия базы данных

        Returns:
            Список уведомлений
        """
        query = select(Notification).where(Notification.user_id == user_id)

        if status:
            query = query.where(Notification.status == status)

        query = query.order_by(Notification.created_at.desc())

        result = db.execute(query)
        notifications = result.scalars().all()
        logger.debug(
            f"Retrieved {len(notifications)} notifications for user {user_id}"
        )
        return list(notifications)
