import uuid


def test_list_documents_requires_auth(client):
    response = client.get("/documents")
    assert response.status_code == 401


def test_upload_document_rejects_unsupported_content_type(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword123"
    client.post("/auth/signup", json={"email": email, "password": password})
    login_response = client.post("/auth/login", data={"username": email, "password": password})
    token = login_response.json()["access_token"]

    response = client.post(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 400
