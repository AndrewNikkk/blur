import importlib
import os
import sys
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _ensure_ml_deps_for_tests() -> None:
    """Provide lightweight stubs for optional ML deps in test env."""
    if "cv2" not in sys.modules:
        cv2_stub = types.ModuleType("cv2")
        cv2_stub.COLOR_BGR2RGB = 0
        cv2_stub.IMREAD_COLOR = 1
        cv2_stub.cvtColor = lambda image, *_args, **_kwargs: image
        cv2_stub.imdecode = lambda *_args, **_kwargs: object()
        cv2_stub.imencode = lambda *_args, **_kwargs: (
            True,
            types.SimpleNamespace(tobytes=lambda: b"encoded"),
        )
        cv2_stub.GaussianBlur = lambda image, *_args, **_kwargs: image
        sys.modules["cv2"] = cv2_stub

    if "numpy" not in sys.modules:
        np_stub = types.ModuleType("numpy")
        np_stub.ndarray = object
        np_stub.uint8 = int
        np_stub.frombuffer = lambda *_args, **_kwargs: b""
        sys.modules["numpy"] = np_stub

    if "ultralytics" not in sys.modules:
        ultra_stub = types.ModuleType("ultralytics")

        class _DummyYOLO:
            def __init__(self, *_args, **_kwargs):
                pass

            def predict(self, *_args, **_kwargs):
                return []

        ultra_stub.YOLO = _DummyYOLO
        sys.modules["ultralytics"] = ultra_stub


_ensure_ml_deps_for_tests()


os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("REFRESH_SECRET_KEY", "test-refresh-secret-key")

from app.core.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def db_session(tmp_path):
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    credentials = {"login": "test_user", "password": "verysecret123"}
    client.post("/auth/register", json=credentials)
    login_response = client.post("/auth/login", json=credentials)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
