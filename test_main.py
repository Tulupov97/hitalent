import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """
    Тест корневого маршрута.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Добро пожаловать в API"}