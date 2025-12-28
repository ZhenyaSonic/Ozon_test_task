FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install fastapi sqlalchemy pydantic-settings uvicorn

COPY . .

ENV PYTHONPATH=/app/src:$PYTHONPATH

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]