import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.models.agent import AgentResponse
from datetime import datetime

client = TestClient(app)

from app.api.routes import get_agent_service

@pytest.fixture
def mock_agent_service():
    mock_service = AsyncMock()
    app.dependency_overrides[get_agent_service] = lambda: mock_service
    yield mock_service
    app.dependency_overrides.clear()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_session(mock_agent_service):
    mock_agent_service.create_session.return_value = "session-123"
    
    response = client.post("/api/sessions", json={"store_url": "https://test-store.myshopify.com"})
    
    assert response.status_code == 200
    assert response.json() == {"session_id": "session-123"}
    mock_agent_service.create_session.assert_called_with("https://test-store.myshopify.com")

def test_create_session_invalid_url(mock_agent_service):
    # Pydantic validation should fail before hitting service
    response = client.post("/api/sessions", json={"store_url": "invalid"})
    
    assert response.status_code == 422
    assert "value_error" in str(response.json()) or "string_pattern_mismatch" in str(response.json())

def test_chat_success(mock_agent_service):
    mock_agent_service.chat.return_value = AgentResponse(
        session_id="session-123",
        message="Here is the data",
        timestamp=datetime.utcnow()
    )
    
    response = client.post("/api/chat", json={
        "session_id": "session-123",
        "message": "show me orders"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "session-123"
    assert data["message"] == "Here is the data"

def test_chat_session_not_found(mock_agent_service):
    mock_agent_service.chat.side_effect = ValueError("Session not found")
    
    response = client.post("/api/chat", json={
        "session_id": "unknown",
        "message": "hello"
    })
    
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]

def test_chat_rate_limit(mock_agent_service):
    mock_agent_service.chat.side_effect = ValueError("Rate limit exceeded")
    
    response = client.post("/api/chat", json={
        "session_id": "session-123",
        "message": "spam"
    })
    
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

def test_get_history(mock_agent_service):
    mock_agent_service.get_history.return_value = [
        {"role": "user", "content": "hi", "timestamp": "2025-12-01T00:00:00Z"},
        {"role": "assistant", "content": "hello", "timestamp": "2025-12-01T00:00:01Z"}
    ]
    
    response = client.get("/api/sessions/session-123/history")
    
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2
    assert history[0]["role"] == "user"
