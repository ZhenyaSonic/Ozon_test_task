from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
from typing import Generator

from core.settings import settings
from logger import logger


Base = declarative_base()


class DatabaseManager:
    """Менеджер подключений к базе данных"""
    def __init__(self):
        self._engine = None
        self._session_factory = None

    def init(self) -> None:
        """Инициализация подключения к базе данных"""
        if not settings.DATABASE_URL:
            database_url = settings.SQLITE_DEFAULT_PATH
            logger.warning("DATABASE_URL not set, using SQLite")
        else:
            database_url = str(settings.DATABASE_URL)
            try:
                logger.info(f"Attempting to connect to PostgreSQL: {database_url}")
                test_engine = create_engine(
                    database_url,
                    pool_pre_ping=True,
                    echo=False,
                    connect_args={"connect_timeout": settings.DATABASE_CONNECT_TIMEOUT}
                )
                with test_engine.connect() as conn:
                    conn.execute(text(settings.DATABASE_HEALTH_CHECK_QUERY))
                logger.info("Successfully connected to PostgreSQL")
            except Exception as e:
                logger.warning(
                    f"Failed to connect to PostgreSQL: {e}. "
                    "Falling back to SQLite"
                )
                database_url = settings.SQLITE_DEFAULT_PATH

        logger.info(f"Initializing database connection: {database_url}")

        self._engine = create_engine(
            database_url,
            pool_pre_ping=True,
            echo=False
        )

        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

        self.create_tables()

    def create_tables(self) -> None:
        """Создание таблиц в базе данных"""
        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Контекстный менеджер для получения сессии"""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")

        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Закрытие соединений с базой данных"""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connections closed")


db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """Зависимость для получения сессии БД (используется в FastAPI)"""
    with db_manager.get_session() as session:
        yield session
