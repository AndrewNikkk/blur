from pathlib import Path

import pytest

from app.core import storage


@pytest.mark.unit
def test_save_uploaded_file_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "UPLOADS_DIR", tmp_path / "uploads")
    storage.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    filename, file_path = storage.save_uploaded_file(b"abc", "sample.jpg")

    assert filename.endswith(".jpg")
    assert Path(file_path).exists()
    assert Path(file_path).read_bytes() == b"abc"


@pytest.mark.unit
def test_save_uploaded_file_without_name_uses_default(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "UPLOADS_DIR", tmp_path / "uploads")
    storage.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    filename, file_path = storage.save_uploaded_file(b"abc", None)

    assert filename
    assert Path(file_path).exists()


@pytest.mark.unit
def test_save_processed_file_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "PROCESSED_DIR", tmp_path / "processed")
    storage.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    file_path = storage.save_processed_file(b"processed", "out.png")

    assert file_path.endswith(".png")
    assert Path(file_path).exists()
    assert Path(file_path).read_bytes() == b"processed"


@pytest.mark.unit
def test_get_file_path_returns_none_for_missing(tmp_path):
    missing = tmp_path / "missing.txt"
    assert storage.get_file_path(str(missing)) is None


@pytest.mark.unit
def test_delete_file_true_when_exists(tmp_path):
    target = tmp_path / "to-delete.txt"
    target.write_text("x", encoding="utf-8")

    assert storage.delete_file(str(target)) is True
    assert not target.exists()


@pytest.mark.unit
def test_delete_file_false_when_missing(tmp_path):
    target = tmp_path / "not-exists.txt"
    assert storage.delete_file(str(target)) is False
