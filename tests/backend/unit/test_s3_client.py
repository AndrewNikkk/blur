from types import SimpleNamespace

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import HTTPException

from app.core.s3 import LazyS3Client


class _DummyS3:
    def __init__(self):
        self.uploaded = False
        self.deleted = False
        self.created_bucket = False

    def head_bucket(self, Bucket):  # noqa: N803
        return {"Bucket": Bucket}

    def create_bucket(self, Bucket):  # noqa: N803
        self.created_bucket = True
        return {"Bucket": Bucket}

    def upload_fileobj(self, *_args, **_kwargs):
        self.uploaded = True

    def generate_presigned_url(self, *_args, **_kwargs):
        return "http://example.com/presigned"

    def delete_object(self, *_args, **_kwargs):
        self.deleted = True
        return {}


@pytest.mark.unit
def test_client_property_initializes_and_checks_bucket(monkeypatch):
    dummy = _DummyS3()
    monkeypatch.setattr("app.core.s3.boto3.client", lambda *_args, **_kwargs: dummy)

    client = LazyS3Client()
    actual = client.client

    assert actual is dummy


@pytest.mark.unit
def test_client_property_raises_runtime_error_on_endpoint_failure(monkeypatch):
    def _raise_endpoint_error(*_args, **_kwargs):
        raise EndpointConnectionError(endpoint_url="http://localhost:9000")

    monkeypatch.setattr("app.core.s3.boto3.client", _raise_endpoint_error)

    with pytest.raises(RuntimeError):
        _ = LazyS3Client().client


@pytest.mark.unit
def test_ensure_bucket_exists_creates_bucket_on_404():
    client = LazyS3Client()
    dummy = _DummyS3()

    def _head_bucket_fail(Bucket):  # noqa: N803
        raise ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadBucket")

    dummy.head_bucket = _head_bucket_fail
    client._client = dummy
    client._ensure_bucket_exists()

    assert dummy.created_bucket is True


@pytest.mark.unit
def test_upload_file_success():
    client = LazyS3Client()
    dummy = _DummyS3()
    client._client = dummy

    result = client.upload_file(file_data=SimpleNamespace(), object_name="k", content_type="image/jpeg")
    assert result == "k"
    assert dummy.uploaded is True


@pytest.mark.unit
def test_upload_file_raises_http_503_on_endpoint_error():
    client = LazyS3Client()

    class _BrokenS3:
        def upload_fileobj(self, *_args, **_kwargs):
            raise EndpointConnectionError(endpoint_url="http://localhost:9000")

    client._client = _BrokenS3()

    with pytest.raises(HTTPException) as exc:
        client.upload_file(file_data=SimpleNamespace(), object_name="k", content_type="image/jpeg")
    assert exc.value.status_code == 503


@pytest.mark.unit
def test_get_presigned_url_success():
    client = LazyS3Client()
    client._client = _DummyS3()
    url = client.get_presigned_url("obj-key")
    assert url.startswith("http://example.com")


@pytest.mark.unit
def test_delete_file_no_such_key_is_true():
    client = LazyS3Client()

    class _NoSuchKeyClient:
        def delete_object(self, *_args, **_kwargs):
            raise ClientError({"Error": {"Code": "NoSuchKey", "Message": "No key"}}, "DeleteObject")

    client._client = _NoSuchKeyClient()
    assert client.delete_file("missing-key") is True
