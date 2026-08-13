import uuid


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def test_signup_and_login(client):
    email = _unique_email()
    password = "testpassword123"

    signup_response = client.post("/auth/signup", json={"email": email, "password": password})
    assert signup_response.status_code == 201
    assert signup_response.json()["email"] == email

    login_response = client.post("/auth/login", data={"username": email, "password": password})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_signup_duplicate_email_fails(client):
    email = _unique_email()
    password = "testpassword123"

    client.post("/auth/signup", json={"email": email, "password": password})
    second_response = client.post("/auth/signup", json={"email": email, "password": password})
    assert second_response.status_code == 400


def test_login_wrong_password_fails(client):
    email = _unique_email()
    password = "testpassword123"

    client.post("/auth/signup", json={"email": email, "password": password})
    login_response = client.post("/auth/login", data={"username": email, "password": "wrongpassword"})
    assert login_response.status_code == 401


def test_me_requires_auth(client):
    email = _unique_email()
    password = "testpassword123"

    client.post("/auth/signup", json={"email": email, "password": password})
    login_response = client.post("/auth/login", data={"username": email, "password": password})
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email

    unauthenticated_response = client.get("/auth/me")
    assert unauthenticated_response.status_code == 401
