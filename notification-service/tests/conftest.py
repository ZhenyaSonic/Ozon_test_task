"""Фикстуры для тестов"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.core.constants import TEST_USER_ID, TEST_MESSAGE_CODE
from src.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Фикстура на уровне сессии для инициализации базы данных.
    Убеждаемся, что база данных инициализирована только один раз.
    """
    Base.metadata.clear()


@pytest.fixture(scope="function")
def db_session():
    """Создание тестовой базы данных в памяти"""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    session = TestingSessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Создание тестового клиента FastAPI"""
    def override_get_db():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise
        finally:
            pass

    original_get_db = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    if original_get_db is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = original_get_db


@pytest.fixture
def notification_data():
    """Тестовые данные для уведомления"""
    return {
        "user_id": TEST_USER_ID,
        "message": f"Ваш код: {TEST_MESSAGE_CODE}",
        "type": "telegram"
    }
