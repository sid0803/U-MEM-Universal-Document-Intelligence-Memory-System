import uuid
from unittest.mock import patch


def test_document_qa_success(client):
    # 1️⃣ Register user (unique email)
    email = f"{uuid.uuid4()}@example.com"

    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "pass1234"
    })

    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2️⃣ Upload document
    upload = client.post(
        "/api/v1/upload/",
        headers=headers,
        files={"file": ("doc.txt", b"This document talks about AI systems.")}
    )

    assert upload.status_code == 202

    # 3️⃣ Get doc_id
    docs = client.get("/api/v1/documents/", headers=headers).json()
    doc_id = docs["documents"][0]["doc_id"]

    # 4️⃣ Mock BOTH semantic_search and ask_llm
    with patch("app.services.document_qa.semantic_search") as mock_search, \
         patch("app.services.document_qa.ask_llm") as mock_llm:

        mock_search.return_value = [{
            "doc_id": doc_id,
            "matched_chunks": [
                {"text": "This document talks about AI systems."}
            ]
        }]

        mock_llm.return_value = "This document discusses AI."

        response = client.post(
            f"/api/v1/documents/{doc_id}/qa",
            headers=headers,
            json={"question": "What is this document about?"}
        )

    assert response.status_code == 200
    data = response.json()

    assert data["doc_id"] == doc_id
    assert "answer" in data
    assert data["sources_used"] >= 1


def test_document_qa_no_results(client):
    email = f"{uuid.uuid4()}@example.com"

    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "pass1234"
    })

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Mock semantic search to return empty
    with patch("app.services.document_qa.semantic_search") as mock_search:
        mock_search.return_value = []

        response = client.post(
            "/api/v1/documents/fake-id/qa",
            headers=headers,
            json={"question": "Test?"}
        )

    assert response.status_code in (400, 404)
