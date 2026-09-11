from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_stats_shape():
    r = client.get("/stats")
    assert r.status_code == 200
    assert "occupied_pct" in r.json()

def test_history_limit():
    r = client.get("/history?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
