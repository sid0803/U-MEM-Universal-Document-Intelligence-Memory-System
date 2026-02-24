import uuid
from unittest.mock import patch


def test_document_summary_endpoint(client):
    email = f"{uuid.uuid4()}@example.com"

    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "pass1234"
    })

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload document
    upload = client.post(
        "/api/v1/upload/",
        headers=headers,
        files={"file": ("doc.txt", b"This document is about AI and machine learning")}
    )

    # Get documents
    docs = client.get("/api/v1/documents/", headers=headers).json()
    doc_id = docs["documents"][0]["doc_id"]

    with patch("app.services.document_summarizer.ask_llm") as mock_llm:
        mock_llm.return_value = "This document discusses AI."

        response = client.post(
            f"/api/v1/documents/{doc_id}/summary",
            headers=headers
        )

    assert response.status_code == 200
    data = response.json()

    assert data["doc_id"] == doc_id
    assert "summary" in data