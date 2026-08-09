import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.src.main import app


class FailingRagChain:
    def invoke(self, question):
        raise Exception("401 Unauthorized: invalid API key")


def test_query_returns_503_for_authentication_errors():
    client = TestClient(app)
    app.state.rag_chain = FailingRagChain()
    app.state.vector_store = object()

    response = client.post("/query", json={"question": "hello"})

    assert response.status_code == 503
    assert "groq" in response.json()["detail"].lower()
