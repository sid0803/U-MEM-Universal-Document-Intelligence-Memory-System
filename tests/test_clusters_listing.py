import uuid
import time


def test_cluster_listing(client):
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
        files={"file": ("doc.txt", b"Machine learning clustering test")}
    )

    time.sleep(0.3)

    # Run clustering
    client.post("/api/v1/clusters/run", headers=headers)

    time.sleep(0.3)

    # List clusters
    response = client.get("/api/v1/clusters/", headers=headers)

    assert response.status_code == 200
    clusters = response.json()

    assert isinstance(clusters, list)