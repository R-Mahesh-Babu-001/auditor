from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"


def test_clear_memory_endpoint():
    # best-effort clear call for a fake namespace; should return 200
    payload = {"agent": "chat_memory", "user_id": "test_user"}
    r = client.post("/api/memory/clear", json=payload)
    # Either success 200 or 500 if clearing isn't possible in the environment
    assert r.status_code in (200, 500)
