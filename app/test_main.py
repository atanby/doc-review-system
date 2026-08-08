from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_documents_requires_auth():
    response = client.get("/documents")
    assert response.status_code == 401


def test_register_and_login(reviewer_headers):
    assert "Authorization" in reviewer_headers


def test_create_and_get_document(reviewer_headers):
    create_response = client.post("/documents", json={"filename": "test_file.pdf"}, headers=reviewer_headers)
    assert create_response.status_code == 200
    data = create_response.json()
    assert data["filename"] == "test_file.pdf"
    assert data["status"] == "pending"

    doc_id = data["id"]
    get_response = client.get(f"/documents/{doc_id}", headers=reviewer_headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == doc_id


def test_get_nonexistent_document(reviewer_headers):
    response = client.get("/documents/999999", headers=reviewer_headers)
    assert response.status_code == 404


def test_reviewer_cannot_delete(reviewer_headers):
    create = client.post("/documents", json={"filename": "test.pdf"}, headers=reviewer_headers)
    doc_id = create.json()["id"]

    delete_response = client.delete(f"/documents/{doc_id}", headers=reviewer_headers)
    assert delete_response.status_code == 403


def test_admin_can_delete(admin_headers):
    create = client.post("/documents", json={"filename": "delete_me.pdf"}, headers=admin_headers)
    doc_id = create.json()["id"]

    delete_response = client.delete(f"/documents/{doc_id}", headers=admin_headers)
    assert delete_response.status_code == 200


def test_classify_document(reviewer_headers):
    create = client.post("/documents", json={"filename": "invoice_test.pdf"}, headers=reviewer_headers)
    doc_id = create.json()["id"]

    response = client.post(
        f"/documents/{doc_id}/classify",
        json={"text": "Invoice number 100 total amount due payment terms"},
        headers=reviewer_headers,
    )
    assert response.status_code == 200
    assert response.json()["document_type"] in ["invoice", "contract", "id_document", "certificate"]


def test_upload_pdf_document(reviewer_headers):
    with open("../tests/sample_invoice.pdf", "rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("sample_invoice.pdf", f, "application/pdf")},
            headers=reviewer_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample_invoice.pdf"
    assert data["extracted_text"] is not None


def test_review_queue_and_history(reviewer_headers):
    create = client.post("/documents", json={"filename": "history_test.pdf"}, headers=reviewer_headers)
    doc_id = create.json()["id"]

    queue_response = client.get("/review-queue", headers=reviewer_headers)
    assert queue_response.status_code == 200
    assert any(d["id"] == doc_id for d in queue_response.json())

    update_response = client.patch(
        f"/documents/{doc_id}/status",
        json={"status": "approved", "comment": "Test approval"},
        headers=reviewer_headers,
    )
    assert update_response.status_code == 200

    history_response = client.get(f"/documents/{doc_id}/history", headers=reviewer_headers)
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["old_status"] == "pending"
    assert history[0]["new_status"] == "approved"
    assert history[0]["comment"] == "Test approval"


def test_invalid_status_rejected(reviewer_headers):
    create = client.post("/documents", json={"filename": "bad_status.pdf"}, headers=reviewer_headers)
    doc_id = create.json()["id"]

    response = client.patch(
        f"/documents/{doc_id}/status",
        json={"status": "not_a_real_status"},
        headers=reviewer_headers,
    )
    assert response.status_code == 422