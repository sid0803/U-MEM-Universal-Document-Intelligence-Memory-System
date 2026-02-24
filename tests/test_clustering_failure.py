import uuid


def test_clustering_without_documents(client):
    email = f"{uuid.uuid4()}@example.com"

    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "pass1234"
    })

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/clusters/run", headers=headers)

    assert response.status_code == 400