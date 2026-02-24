import uuid
import time


def test_user_cannot_access_other_users_clusters(client):
    # User A
    email_a = f"{uuid.uuid4()}@example.com"
    r1 = client.post("/api/v1/auth/register", json={
        "email": email_a,
        "password": "pass1234"
    })
    token_a = r1.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    email_b = f"{uuid.uuid4()}@example.com"
    r2 = client.post("/api/v1/auth/register", json={
        "email": email_b,
        "password": "pass1234"
    })
    token_b = r2.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A uploads document
    client.post(
        "/api/v1/upload/",
        headers=headers_a,
        files={"file": ("doc.txt", b"User A private document")}
    )

    time.sleep(0.3)

    client.post("/api/v1/clusters/run", headers=headers_a)

    time.sleep(0.3)

    clusters_a = client.get("/api/v1/clusters/", headers=headers_a).json()

    if clusters_a:
        cluster_id = clusters_a[0]["cluster_id"]

        # User B tries to access A's cluster
        response = client.get(
            f"/api/v1/clusters/{cluster_id}/documents",
            headers=headers_b
        )

        assert response.status_code in (403, 404)