FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (git optional)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the Streamlit source code
COPY . /app

# Expose Streamlit default port
EXPOSE 8501

# Backend URL defaults to the internal Docker hostname
ENV BACKEND_URL=${BACKEND_URL:-http://backend:8000}

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
