import uuid


def test_summary_invalid_doc(client):
    # 1️⃣ Register user with unique email
    email = f"{uuid.uuid4()}@example.com"

    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "pass1234"
    })

    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2️⃣ Call summary on invalid document
    response = client.post(
        "/api/v1/documents/invalid-id/summary",
        headers=headers
    )

    assert response.status_code == 404
