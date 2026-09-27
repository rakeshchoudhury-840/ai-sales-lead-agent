from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "LeadPilot"


def test_chat():
    response = client.post(
        "/chat",
        json={"session_id": "test-session", "message": "I need office chairs"},
    )
    assert response.status_code == 200
    assert "response" in response.json()
