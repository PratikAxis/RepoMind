import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "RepoMind Backend"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ingest_invalid_source_type():
    response = client.post("/ingest", json={"source_type": "invalid", "path": "/some/path"})
    assert response.status_code == 400
    assert "Invalid source_type" in response.json()["detail"]

def test_ingest_remote_missing_url():
    response = client.post("/ingest", json={"source_type": "remote", "path": "/some/path"})
    assert response.status_code == 400
    assert "URL is required" in response.json()["detail"]

def test_query_before_ingest():
    response = client.post("/query", json={"question": "What is this repo?"})
    assert response.status_code == 400
    assert "RAG chain not initialized" in response.json()["detail"]
