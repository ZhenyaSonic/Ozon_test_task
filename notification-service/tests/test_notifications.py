"""Тесты для API уведомлений"""
import time
from fastapi import status
from typing import Dict, Any

from src.models.notification import NotificationStatus
from src.core.constants import (
    TEST_MAX_RESPONSE_TIME,
    TEST_DELAY,
    TEST_USER_ID,
    TEST_USER_ID_2,
    TEST_USER_ID_3,
    TEST_USER_ID_MULTI_1,
    TEST_USER_ID_MULTI_2,
    TEST_EMPTY_NOTIFICATIONS_COUNT,
    TEST_MIN_NOTIFICATIONS_COUNT
)
from src.core.settings import settings


class TestCreateNotification:
    """Тесты для создания уведомлений"""

    def test_create_notification_success(self, client, notification_data):
        """Тест успешного создания уведомления"""
        response = client.post("/api/notifications", json=notification_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["user_id"] == notification_data["user_id"]
        assert data["message"] == notification_data["message"]
        assert data["type"] == notification_data["type"]
        assert data["status"] == NotificationStatus.PENDING.value
        assert data["attempts"] == settings.NOTIFICATION_INITIAL_ATTEMPTS
        assert "id" in data
        assert "created_at" in data

    def test_create_notification_async_response(self, client, notification_data):
        """Тест, что ответ приходит сразу, не дожидаясь отправки"""
        start_time = time.time()
        response = client.post("/api/notifications", json=notification_data)
        response_time = time.time() - start_time

        assert response_time < TEST_MAX_RESPONSE_TIME
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == NotificationStatus.PENDING.value

    def test_create_notification_email_type(self, client):
        """Тест создания уведомления типа email"""
        notification_data = {
            "user_id": TEST_USER_ID_2,
            "message": "Test email message",
            "type": "email"
        }

        response = client.post("/api/notifications", json=notification_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["type"] == "email"

    def test_create_notification_validation_error(self, client):
        """Тест валидации данных при создании уведомления"""
        invalid_data = {"user_id": TEST_USER_ID}
        response = client.post("/api/notifications", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetNotifications:
    """Тесты для получения истории уведомлений"""

    def test_get_notifications_empty_list(self, client):
        """Тест получения пустого списка уведомлений"""
        response = client.get(f"/api/notifications/{TEST_USER_ID_3}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == TEST_EMPTY_NOTIFICATIONS_COUNT
        assert data["notifications"] == []

    def test_get_notifications_with_data(self, client, notification_data):
        """Тест получения уведомлений пользователя"""
        create_response = client.post("/api/notifications", json=notification_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        time.sleep(TEST_DELAY)

        response = client.get(f"/api/notifications/{notification_data['user_id']}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total"] >= TEST_MIN_NOTIFICATIONS_COUNT
        assert len(data["notifications"]) >= TEST_MIN_NOTIFICATIONS_COUNT
        assert data["notifications"][0]["user_id"] == notification_data["user_id"]

    def test_get_notifications_filter_by_status(self, client, notification_data):
        """Тест фильтрации уведомлений по статусу"""
        create_response = client.post("/api/notifications", json=notification_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        response = client.get(
            f"/api/notifications/{notification_data['user_id']}",
            params={"status": NotificationStatus.PENDING.value}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        for notification in data["notifications"]:
            assert notification["status"] == NotificationStatus.PENDING.value

        time.sleep(TEST_DELAY * 20)

        response_sent = client.get(
            f"/api/notifications/{notification_data['user_id']}",
            params={"status": NotificationStatus.SENT.value}
        )
        assert response_sent.status_code == status.HTTP_200_OK
        data_sent = response_sent.json()

        assert data_sent["total"] >= TEST_MIN_NOTIFICATIONS_COUNT, "Ожидается хотя бы одно отправленное уведомление"
        for notification in data_sent["notifications"]:
            assert notification["status"] == NotificationStatus.SENT.value

    def test_get_notifications_multiple_users(self, client):
        """Тест, что уведомления одного пользователя не видны другому"""
        user1_data = {
            "user_id": TEST_USER_ID_MULTI_1,
            "message": "Message for user 1",
            "type": "telegram"
        }
        user2_data = {
            "user_id": TEST_USER_ID_MULTI_2,
            "message": "Message for user 2",
            "type": "telegram"
        }

        client.post("/api/notifications", json=user1_data)
        client.post("/api/notifications", json=user2_data)

        time.sleep(TEST_DELAY)

        response = client.get(f"/api/notifications/{TEST_USER_ID_MULTI_1}")
        data = response.json()

        for notification in data["notifications"]:
            assert notification["user_id"] == TEST_USER_ID_MULTI_1


class TestHealthEndpoints:
    """Тесты для health check endpoints"""
    def test_root_endpoint(self, client):
        """Тест корневого endpoint"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
