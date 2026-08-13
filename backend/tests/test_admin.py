import uuid


def _signup_and_login(client) -> str:
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword123"
    client.post("/auth/signup", json={"email": email, "password": password})
    login_response = client.post("/auth/login", data={"username": email, "password": password})
    return login_response.json()["access_token"]


def test_admin_users_requires_auth(client):
    response = client.get("/admin/users")
    assert response.status_code == 401


def test_admin_users_requires_admin_role(client):
    token = _signup_and_login(client)
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
