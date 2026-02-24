import uuid


def test_jobs_endpoint_returns_jobs(client):
    email = f"{uuid.uuid4()}@example.com"

    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "pass1234"
    })

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload document to create job
    client.post(
        "/api/v1/upload/",
        headers=headers,
        files={"file": ("doc.txt", b"Job test document")}
    )

    response = client.get("/api/v1/jobs/", headers=headers)

    assert response.status_code == 200

    data = response.json()
    jobs = data if isinstance(data, list) else data.get("jobs", [])

    assert len(jobs) >= 1