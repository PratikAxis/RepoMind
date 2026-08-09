FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (git optional)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU-only first to avoid massive CUDA downloads
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install backend Python dependencies
COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source code (including configs)
COPY . /app/backend

ENV PYTHONPATH=/app:/app/backend

EXPOSE 8000

CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
