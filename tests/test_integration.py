import os
import requests
import sys

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501").rstrip("/")

def test_backend_health():
    url = f"{BACKEND_URL}/health"
    print(f"Testing Backend Health: {url}")
    res = requests.get(url, timeout=5)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert data.get("status") == "ok", f"Expected status 'ok', got {data}"
    print("✅ Backend Health Check Passed!")

def test_frontend_availability():
    print(f"Testing Frontend UI Availability: {FRONTEND_URL}")
    res = requests.get(FRONTEND_URL, timeout=5)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "Streamlit" in res.text or "RepoMind" in res.text or "<!DOCTYPE html>" in res.text
    print("✅ Frontend Availability Check Passed!")

def test_backend_validation_routes():
    print("Testing Backend Invalid Ingest validation...")
    res = requests.post(f"{BACKEND_URL}/ingest", json={"source_type": "invalid", "path": "test"}, timeout=5)
    assert res.status_code == 400
    print("✅ Backend Validation Passed!")

if __name__ == "__main__":
    try:
        test_backend_health()
        test_frontend_availability()
        test_backend_validation_routes()
        print("\n🎉 ALL DOCKER INTEGRATION TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
