#!/bin/sh
set -e

git config --global --add safe.directory /workspace || true

echo "Starting RepoMind Backend API on 127.0.0.1:8000..."
uvicorn backend.src.main:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Render injects PORT env variable. Listen on it if defined, otherwise default to 8501.
TARGET_PORT=${PORT:-8501}
echo "Starting RepoMind Frontend UI on port $TARGET_PORT..."
streamlit run frontend/app.py --server.port "$TARGET_PORT" --server.address 0.0.0.0 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

while kill -0 "$BACKEND_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
    sleep 1
 done

if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "Backend process failed. Exiting container..."
    cat /tmp/backend.log
    exit 1
fi

if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo "Frontend process failed. Exiting container..."
    cat /tmp/frontend.log
    exit 1
fi

exit 0
