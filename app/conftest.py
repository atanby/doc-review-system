import pytest
import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def reviewer_headers():
    username = f"reviewer_{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username, "password": "pass12345", "role": "reviewer"})
    login = client.post("/login", data={"username": username, "password": "pass12345"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers():
    username = f"admin_{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username, "password": "pass12345", "role": "admin"})
    login = client.post("/login", data={"username": username, "password": "pass12345"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}