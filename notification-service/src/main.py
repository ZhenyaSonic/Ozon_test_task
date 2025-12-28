"""Главный файл приложения FastAPI"""
import time
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.settings import settings
from core.database import db_manager
from core.constants import (
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    EXIT_CODE_SUCCESS
)
from routers.notifications import router as notifications_router
from logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    Обрабатывает инициализацию и graceful shutdown
    """
    logger.info("Starting notification service...")
    db_manager.init()
    logger.info(
        f"Notification service started successfully. "
        f"Access the API at http://localhost:{settings.APP_PORT} "
        f"or http://{settings.LOCALHOST_IP}:{settings.APP_PORT}"
    )

    yield

    logger.info("Shutting down notification service...")
    db_manager.close()
    logger.info("Notification service stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Smart Notification System - микросервис для управления рассылками"
    ),
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware для логирования HTTP запросов
    Логирует метод, путь, статус код и время обработки
    """
    start_time = time.time()

    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None
        }
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        time_format = f".{settings.TIME_FORMAT_DECIMAL_PLACES}f"
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {format(process_time, time_format)}s",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time
            }
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time
        time_format = f".{settings.TIME_FORMAT_DECIMAL_PLACES}f"
        logger.error(
            f"Request failed: {request.method} {request.url.path} - "
            f"Error: {str(e)} - Time: {format(process_time, time_format)}s",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "process_time": process_time
            },
            exc_info=True
        )
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True
    )
    return JSONResponse(
        status_code=HTTP_STATUS_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


app.include_router(notifications_router)


@app.get("/", tags=["health"])
async def root():
    """Корневой endpoint для проверки работоспособности"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


def signal_handler(sig, frame):
    """Обработчик сигналов SIGINT и SIGTERM"""
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    sys.exit(EXIT_CODE_SUCCESS)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_config=None,
        reload=settings.DEBUG
    )
