import pytest


def _register_and_login(client, login: str, password: str):
    payload = {"login": login, "password": password}
    client.post("/auth/register", json=payload)
    token = client.post("/auth/login", json=payload).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_profile_requires_auth(client):
    response = client.get("/profile")
    assert response.status_code == 403


@pytest.mark.integration
def test_get_profile_returns_current_user(client):
    headers = _register_and_login(client, "profile_user", "profilepass123")
    response = client.get("/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["login"] == "profile_user"


@pytest.mark.integration
def test_profile_files_paginated_metadata(client, monkeypatch):
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)
    headers = _register_and_login(client, "pf_user", "pfpass123")

    client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("pf.jpg", b"img", "image/jpeg")},
    )

    response = client.get("/profile/files/paginated?page=1&per_page=10", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert "total_pages" in payload


@pytest.mark.integration
def test_profile_file_forbidden_for_other_user(client, monkeypatch):
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)
    headers_1 = _register_and_login(client, "owner_profile", "ownerpass123")
    headers_2 = _register_and_login(client, "other_profile", "otherpass123")

    upload = client.post(
        "/files/upload",
        headers=headers_1,
        files={"file": ("a.jpg", b"img", "image/jpeg")},
    )
    file_id = upload.json()["id"]

    response = client.get(f"/profile/files/{file_id}", headers=headers_2)
    assert response.status_code == 403


@pytest.mark.integration
def test_change_password_success_and_fail_old_password(client):
    headers = _register_and_login(client, "settings_user", "oldpass123")

    bad = client.put(
        "/settings/password",
        headers=headers,
        json={"old_password": "wrongpass", "new_password": "newpass123"},
    )
    assert bad.status_code == 400

    good = client.put(
        "/settings/password",
        headers=headers,
        json={"old_password": "oldpass123", "new_password": "newpass123"},
    )
    assert good.status_code == 200

    relogin = client.post("/auth/login", json={"login": "settings_user", "password": "newpass123"})
    assert relogin.status_code == 200


@pytest.mark.integration
def test_delete_account_removes_user(client, monkeypatch):
    monkeypatch.setattr("app.routers.settings.delete_file", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)

    headers = _register_and_login(client, "delete_user", "deletepass123")
    client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("to-delete.jpg", b"img", "image/jpeg")},
    )

    delete_response = client.delete("/settings/account", headers=headers)
    assert delete_response.status_code == 200

    login_again = client.post("/auth/login", json={"login": "delete_user", "password": "deletepass123"})
    assert login_again.status_code == 401
