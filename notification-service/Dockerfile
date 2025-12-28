FROM python:3.11-slim

RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

USER appuser

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    LOG_LEVEL=INFO \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

COPY . .

RUN mkdir -p /app/data && chmod 755 /app/data

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["sh", "-c", "cd /app/src && python -m uvicorn main:app --host 0.0.0.0 --port 8000"]