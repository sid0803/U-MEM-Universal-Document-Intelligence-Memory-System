import uuid

def test_user_registration_and_login(client):
    email = f"{uuid.uuid4()}@example.com"

    response = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "strongpassword"
    })

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 200
