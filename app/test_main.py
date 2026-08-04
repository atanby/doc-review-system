from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_get_document():
    create_response = client.post("/documents", json={"filename": "test_file.pdf"})
    assert create_response.status_code == 200
    data = create_response.json()
    assert data["filename"] == "test_file.pdf"
    assert data["status"] == "pending"

    doc_id = data["id"]
    get_response = client.get(f"/documents/{doc_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == doc_id

def test_get_nonexistent_document():
    response = client.get("/documents/999999")
    assert response.status_code == 404