# Smart Notification System

Микросервис для управления рассылками уведомлений (Email/Telegram) с асинхронной обработкой и retry механизмом.

## Возможности

- Создание уведомлений (Email/Telegram) с асинхронной отправкой
- Получение истории уведомлений пользователя
- Фильтрация уведомлений по статусу
- Retry механизм с настраиваемым количеством попыток
- Логирование всех запросов и операций
- Поддержка PostgreSQL и SQLite
- Graceful shutdown
- Полная документация API через Swagger/OpenAPI

## Технический стек

- **Python 3.11+**
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **PostgreSQL/SQLite** - база данных
- **Pydantic** - валидация данных
- **Pytest** - тестирование

## Архитектура

Проект следует принципам Clean Architecture и разделен на следующие слои:

```
notification-service/
├── src/
│   ├── core/           # Ядро приложения (настройки, БД)
│   ├── models/         # SQLAlchemy модели
│   ├── schemas/        # Pydantic схемы для валидации
│   ├── services/       # Бизнес-логика
│   ├── routers/        # API endpoints
│   ├── logger.py       # Настройка логирования
│   └── main.py         # Точка входа приложения
├── tests/              # Unit-тесты
├── Dockerfile          # Образ для контейнеризации
├── docker-compose.yml  # Оркестрация сервисов
└── pyproject.toml      # Зависимости проекта
```

## Установка и запуск

### Локальный запуск

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd notification-service
```

2. **Установите зависимости:**
```bash
pip install -e .
```

3. **Настройте переменные окружения (опционально):**
Создайте файл `.env` на основе env.example в корне проекта:

4. **Запустите приложение:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Приложение будет доступно по адресам:
- `http://localhost:8000`
- `http://127.0.0.1:8000`

**Важно:** Если сервер запущен на `0.0.0.0`, используйте `localhost` или `127.0.0.1` в браузере, а не `0.0.0.0`.

**Проверка работоспособности:**
- Главная страница: `http://localhost:8000`
- Health check: `http://localhost:8000/health`
- Swagger документация: `http://localhost:8000/docs`
- ReDoc документация: `http://localhost:8000/redoc`

### Запуск через Docker

1. **Сборка и запуск через Docker:**
```bash
docker build -t notification-service . && docker run -p 8000:8000 notification-service
```

2. **Запуск через Docker Compose (с PostgreSQL):**
```bash
docker-compose up -d
```

Docker Compose автоматически:
- Поднимет PostgreSQL базу данных
- Создаст необходимые таблицы
- Запустит приложение

## Запуск тестов

```bash
# Установка dev зависимостей
pip install -e ".[dev]"

# Запуск тестов
pytest tests/ -v

# Запуск тестов с покрытием
pytest tests/ -v --cov=src --cov-report=html
```

## API Документация

После запуска приложения доступна интерактивная документация:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## API Endpoints

### POST /api/notifications
Создает новое уведомление и запускает его отправку в фоновом режиме.

**Запрос:**
```json
{
  "user_id": 123,
  "message": "Ваш код: 1111",
  "type": "telegram"
}
```

**Ответ:** 201 Created
```json
{
  "id": 1,
  "user_id": 123,
  "message": "Ваш код: 1111",
  "type": "telegram",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "attempts": 0
}
```

### GET /api/notifications/{user_id}
Получает историю уведомлений пользователя.

**Query параметры:**
- `status_filter` (опционально): `pending`, `sent`, `failed`

**Пример:**
```bash
GET /api/notifications/123?status_filter=sent
```

**Ответ:** 200 OK
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 123,
      "message": "Ваш код: 1111",
      "type": "telegram",
      "status": "sent",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:01",
      "attempts": 1
    }
  ],
  "total": 1
}
```

## ⚙️ Конфигурация

Все настройки приложения управляются через переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `LOG_LEVEL` | Уровень логирования (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `LOG_FORMAT` | Формат логов (json, text) | `json` |
| `APP_HOST` | Хост приложения | `0.0.0.0` |
| `APP_PORT` | Порт приложения | `8000` |
| `DATABASE_URL` | URL подключения к PostgreSQL | `None` (используется SQLite) |
| `EMAIL_DELAY` | Задержка отправки email (секунды) | `1.0` |
| `TELEGRAM_DELAY` | Задержка отправки telegram (секунды) | `0.2` |
| `RETRY_MAX_ATTEMPTS` | Максимальное количество попыток отправки | `3` |
| `ERROR_PROBABILITY` | Вероятность ошибки отправки (0.0-1.0) | `0.1` |

## Логирование

Сервис логирует все операции в STDOUT в формате JSON или текста.

Каждая запись содержит:
- Timestamp
- Уровень логирования
- Сообщение
- Метаданные (module, function, line)

Пример лога:
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "message": "Notification 1 created and queued for sending",
  "logger": "notification_service",
  "module": "notifications",
  "function": "create_notification",
  "line": 45
}
```

## Retry механизм

Сервис автоматически повторяет отправку уведомления при ошибке:
- Вероятность ошибки: 10% (настраивается через `ERROR_PROBABILITY`)
- Максимальное количество попыток: 3 (настраивается через `RETRY_MAX_ATTEMPTS`)
- После исчерпания попыток статус меняется на `failed`

## Архитектурные решения

1. **Разделение ответственности:**
   - Models - работа с БД
   - Schemas - валидация данных
   - Services - бизнес-логика
   - Routers - обработка HTTP запросов

2. **Асинхронность:**
   - Использование FastAPI BackgroundTasks для неблокирующей отправки
   - Клиент получает ответ сразу, отправка происходит в фоне

3. **База данных:**
   - Поддержка PostgreSQL и SQLite
   - Автоматическое создание таблиц при старте
   - Использование SQLAlchemy ORM

4. **Обработка ошибок:**
   - Глобальный exception handler
   - Детальное логирование ошибок
   - Graceful shutdown при получении сигналов

Этот проект создан в рамках тестового задания.
