def test_unauthorized_access(client):
    response = client.get("/api/v1/jobs/")
    assert response.status_code == 401