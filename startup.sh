#!/bin/sh
set -e

git config --global --add safe.directory /workspace || true

echo "Starting RepoMind Backend API on port 8000..."
uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 &

echo "Starting RepoMind Frontend UI on port 8501..."
exec streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
