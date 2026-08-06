#!/bin/sh
set -e

git config --global --add safe.directory /workspace || true

echo "Starting RepoMind Backend API on port 8000..."
uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting RepoMind Frontend UI on port 8501..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 > /tmp/frontend.log 2>&1 &
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
