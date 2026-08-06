from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_document():
    client.post("/register", json={"username": "testuser3", "password": "pass123", "role": "reviewer"})
    login = client.post("/login", data={"username": "testuser3", "password": "pass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post("/documents", json={"filename": "test_file.pdf"}, headers=headers)
    assert create_response.status_code == 200
    data = create_response.json()
    assert data["filename"] == "test_file.pdf"
    assert data["status"] == "pending"

    doc_id = data["id"]
    get_response = client.get(f"/documents/{doc_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == doc_id


def test_get_nonexistent_document():
    client.post("/register", json={"username": "testuser4", "password": "pass123", "role": "reviewer"})
    login = client.post("/login", data={"username": "testuser4", "password": "pass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/documents/999999", headers=headers)
    assert response.status_code == 404


def test_register_and_login():
    client.post("/register", json={"username": "testuser1", "password": "pass123", "role": "reviewer"})
    response = client.post("/login", data={"username": "testuser1", "password": "pass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_documents_requires_auth():
    response = client.get("/documents")
    assert response.status_code == 401


def test_reviewer_cannot_delete():
    client.post("/register", json={"username": "testuser2", "password": "pass123", "role": "reviewer"})
    login = client.post("/login", data={"username": "testuser2", "password": "pass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post("/documents", json={"filename": "test.pdf"}, headers=headers)
    doc_id = create.json()["id"]

    delete_response = client.delete(f"/documents/{doc_id}", headers=headers)
    assert delete_response.status_code == 403


def test_classify_document():
    client.post("/register", json={"username": "testuser5", "password": "pass123", "role": "reviewer"})
    login = client.post("/login", data={"username": "testuser5", "password": "pass123"})
    token = login.json()["access_token"]
def test_review_queue_and_history():
    client.post("/register", json={"username": "testuser7", "password": "pass123", "role": "reviewer"})
    login = client.post("/login", data={"username": "testuser7", "password": "pass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post("/documents", json={"filename": "history_test.pdf"}, headers=headers)
    doc_id = create.json()["id"]

    queue_response = client.get("/review-queue", headers=headers)
    assert queue_response.status_code == 200
    assert any(d["id"] == doc_id for d in queue_response.json())

    update_response = client.patch(
        f"/documents/{doc_id}/status",
        json={"status": "approved", "comment": "Test approval"},
        headers=headers,
    )
    assert update_response.status_code == 200

    history_response = client.get(f"/documents/{doc_id}/history", headers=headers)
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["old_status"] == "pending"
    assert history[0]["new_status"] == "approved"
    assert history[0]["comment"] == "Test approval"