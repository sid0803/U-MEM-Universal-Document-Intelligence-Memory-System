import uuid
import time


def test_clustering_lifecycle(client):
    # 1️⃣ Register user
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
        files={"file": ("test.txt", b"AI clustering test document")}
    )

    assert upload.status_code == 202

    # 3️⃣ Run clustering
    run = client.post("/api/v1/clusters/run", headers=headers)
    assert run.status_code == 200

    job_id = run.json()["job_id"]

    # 4️⃣ Poll job until SUCCESS
    job = None

    for _ in range(15):  # give it enough time
        response = client.get("/api/v1/jobs/", headers=headers)
        assert response.status_code == 200

        data = response.json()

        # Handle both list and dict formats safely
        jobs = data if isinstance(data, list) else data.get("jobs", [])

        job = next((j for j in jobs if j["job_id"] == job_id), None)

        if job and job["status"] == "SUCCESS":
            break

        time.sleep(0.2)

    assert job is not None
    assert job["status"] == "SUCCESS"