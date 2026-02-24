import uuid
import time

def test_upload_creates_vectors(client):
    email = f"{uuid.uuid4()}@example.com"

    # 1️⃣ Register user
    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "pass1234"
    })

    assert r.status_code == 200
    token = r.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 2️⃣ Upload file
    response = client.post(
        "/api/v1/upload/",
        headers=headers,
        files={"file": ("test.txt", b"This is a test document")}
    )

    assert response.status_code == 202

    data = response.json()
    assert "job_id" in data
    assert data["status"] == "running" or data["status"] == "RUNNING"

    # 3️⃣ Give background task time (TestClient runs synchronously,
    # but small sleep helps safety)
    time.sleep(0.2)

    # 4️⃣ Verify vectors exist
    from app.storage.vector_store import index
    assert index.ntotal > 0
