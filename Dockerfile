FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git curl && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
COPY frontend/requirements.txt /app/frontend/requirements.txt

RUN pip install --no-cache-dir -r /app/backend/requirements.txt -r /app/frontend/requirements.txt

COPY backend /app/backend
COPY frontend /app/frontend
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

ENV PYTHONPATH=/app:/app/backend \
    BACKEND_URL=http://127.0.0.1:8000 \
    PYTHONUNBUFFERED=1

# Groq API key can be provided at container runtime
ENV GROQ_API_KEY=

# Expose only the Streamlit port so Render directs incoming web traffic to the frontend UI
EXPOSE 8501

HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

CMD ["/app/startup.sh"]
