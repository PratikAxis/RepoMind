FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY backend/src/requirements.txt /app/backend/src/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/src/requirements.txt

COPY backend /app/backend

ENV PYTHONPATH=/app:/app/backend

EXPOSE 8000

CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
