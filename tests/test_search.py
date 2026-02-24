import uuid
import time

def test_semantic_search_returns_results(client):
    email = f"{uuid.uuid4()}@example.com"

    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "pass1234"
    })

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload document
    client.post(
        "/api/v1/upload/",
        headers=headers,
        files={"file": ("doc.txt", b"This document talks about artificial intelligence")}
    )

    time.sleep(0.3)

    # Search
    response = client.get(
        "/api/v1/search/",
        headers=headers,
        params={"q": "artificial intelligence"}
    )

    assert response.status_code == 200
    results = response.json()

    assert len(results) > 0