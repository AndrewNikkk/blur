import pytest


def _register_and_login(client, login: str, password: str):
    payload = {"login": login, "password": password}
    client.post("/auth/register", json=payload)
    token = client.post("/auth/login", json=payload).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_get_file_not_found(client, auth_headers):
    response = client.get("/files/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.integration
def test_save_file_requires_processed_status(client, monkeypatch):
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)
    headers = _register_and_login(client, "save_user", "savepass123")

    upload = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("raw.jpg", b"img", "image/jpeg")},
    )
    file_id = upload.json()["id"]

    response = client.post(f"/files/{file_id}/save", headers=headers)
    assert response.status_code == 400


@pytest.mark.integration
def test_download_and_view_url_success(client, monkeypatch):
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)
    monkeypatch.setattr(
        "app.routers.files.s3_client.get_presigned_url",
        lambda *_args, **_kwargs: "http://example.com/presigned",
    )
    headers = _register_and_login(client, "url_user", "urlpass123")

    upload = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("url.jpg", b"img", "image/jpeg")},
    )
    file_id = upload.json()["id"]

    d_resp = client.get(f"/files/{file_id}/download-url", headers=headers)
    v_resp = client.get(f"/files/{file_id}/view-url", headers=headers)
    redirect_resp = client.get(f"/files/{file_id}/download", headers=headers, follow_redirects=False)

    assert d_resp.status_code == 200
    assert v_resp.status_code == 200
    assert d_resp.json()["url"].startswith("http://example.com")
    assert redirect_resp.status_code in (302, 307)


@pytest.mark.integration
def test_process_file_success_path(client, monkeypatch):
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)

    def _download_fileobj(Bucket, Key, Fileobj):  # noqa: N803
        Fileobj.write(b"fake-original")
        Fileobj.seek(0)

    class _DummyS3Client:
        @staticmethod
        def download_fileobj(Bucket, Key, Fileobj):  # noqa: N803
            return _download_fileobj(Bucket, Key, Fileobj)

    monkeypatch.setattr("app.routers.files.s3_client._client", _DummyS3Client())
    monkeypatch.setattr(
        "app.routers.files.process_image_with_yolo",
        lambda _raw: b"processed-image",
    )

    headers = _register_and_login(client, "process_user", "processpass123")
    upload = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("img.jpg", b"img", "image/jpeg")},
    )
    file_id = upload.json()["id"]

    response = client.post(f"/files/{file_id}/process", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert response.json()["processed_file_path"] is not None


@pytest.mark.integration
def test_process_file_failure_sets_failed_status(client, monkeypatch):
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)

    def _download_fileobj(Bucket, Key, Fileobj):  # noqa: N803
        Fileobj.write(b"fake-original")
        Fileobj.seek(0)

    class _DummyS3Client:
        @staticmethod
        def download_fileobj(Bucket, Key, Fileobj):  # noqa: N803
            return _download_fileobj(Bucket, Key, Fileobj)

    monkeypatch.setattr("app.routers.files.s3_client._client", _DummyS3Client())
    monkeypatch.setattr("app.routers.files.process_image_with_yolo", lambda _raw: None)

    headers = _register_and_login(client, "process_fail_user", "processfail123")
    upload = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("img2.jpg", b"img", "image/jpeg")},
    )
    file_id = upload.json()["id"]

    response = client.post(f"/files/{file_id}/process", headers=headers)
    assert response.status_code == 500
    assert "Processing failed" in response.json()["detail"]

    file_state = client.get(f"/files/{file_id}", headers=headers).json()
    assert file_state["status"] == "failed"


@pytest.mark.integration
def test_delete_file_endpoint_success(client, monkeypatch):
    monkeypatch.setattr("app.routers.files.s3_client.upload_file", lambda **_kwargs: None)
    monkeypatch.setattr("app.routers.files.s3_client.delete_file", lambda *_args, **_kwargs: None)
    headers = _register_and_login(client, "delete_file_user", "deletefile123")

    upload = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("del.jpg", b"img", "image/jpeg")},
    )
    file_id = upload.json()["id"]

    delete_response = client.delete(f"/files/{file_id}", headers=headers)
    assert delete_response.status_code == 200

    get_response = client.get(f"/files/{file_id}", headers=headers)
    assert get_response.status_code == 404
