import pytest


@pytest.mark.integration
def test_upload_file_anonymous_with_session_and_list(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.files.s3_client.upload_file",
        lambda **_kwargs: None,
    )

    response = client.post(
        "/files/upload",
        headers={"X-Session-ID": "anon-session-1"},
        files={"file": ("example.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["session_id"] == "anon-session-1"

    list_response = client.get("/files", headers={"X-Session-ID": "anon-session-1"})
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


@pytest.mark.integration
def test_list_files_requires_session_for_anonymous(client):
    response = client.get("/files")
    assert response.status_code == 401
    assert "Session ID required" in response.json()["detail"]


@pytest.mark.integration
def test_download_url_forbidden_for_another_user(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.files.s3_client.upload_file",
        lambda **_kwargs: None,
    )

    first_user = {"login": "u1", "password": "u1password123"}
    second_user = {"login": "u2", "password": "u2password123"}
    client.post("/auth/register", json=first_user)
    client.post("/auth/register", json=second_user)

    token_1 = client.post("/auth/login", json=first_user).json()["access_token"]
    token_2 = client.post("/auth/login", json=second_user).json()["access_token"]
    headers_1 = {"Authorization": f"Bearer {token_1}"}
    headers_2 = {"Authorization": f"Bearer {token_2}"}

    upload_response = client.post(
        "/files/upload",
        headers=headers_1,
        files={"file": ("owner.jpg", b"owner-bytes", "image/jpeg")},
    )
    file_id = upload_response.json()["id"]

    forbidden_response = client.get(f"/files/{file_id}/download-url", headers=headers_2)
    assert forbidden_response.status_code == 403


@pytest.mark.integration
def test_process_non_image_returns_400(client, monkeypatch):
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)

    user = {"login": "imguser", "password": "imguser123"}
    client.post("/auth/register", json=user)
    token = client.post("/auth/login", json=user).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    upload_response = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("notes.txt", b"text-file", "text/plain")},
    )
    file_id = upload_response.json()["id"]

    process_response = client.post(f"/files/{file_id}/process", headers=headers)
    assert process_response.status_code == 400
    assert "Only image files can be processed" in process_response.json()["detail"]
