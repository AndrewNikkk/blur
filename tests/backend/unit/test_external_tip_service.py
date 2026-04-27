from urllib.error import URLError

import pytest

from app.services import external_tip_service as svc


@pytest.mark.unit
def test_fetch_privacy_tip_returns_fallback_without_api_key(monkeypatch):
    monkeypatch.setattr(svc.settings, "EXTERNAL_TIP_API_KEY", "")
    monkeypatch.setattr(svc, "_cached_tip", None)
    monkeypatch.setattr(svc, "_cached_at", None)

    tip = svc.fetch_privacy_tip()

    assert tip["fallback"] is True
    assert tip["source"] == "local-fallback"
    assert "content" in tip


@pytest.mark.unit
def test_fetch_privacy_tip_uses_cache(monkeypatch):
    monkeypatch.setattr(svc.settings, "EXTERNAL_TIP_API_KEY", "")
    monkeypatch.setattr(svc, "_cached_tip", None)
    monkeypatch.setattr(svc, "_cached_at", None)

    first = svc.fetch_privacy_tip()
    second = svc.fetch_privacy_tip()

    assert first["source"] == second["source"]
    assert first["content"] == second["content"]


@pytest.mark.unit
def test_fetch_privacy_tip_fallback_on_network_error(monkeypatch):
    monkeypatch.setattr(svc.settings, "EXTERNAL_TIP_API_KEY", "dummy")
    monkeypatch.setattr(svc.settings, "EXTERNAL_TIP_MAX_RETRIES", 0)
    monkeypatch.setattr(svc, "_cached_tip", None)
    monkeypatch.setattr(svc, "_cached_at", None)

    def _raise_url_error(*_args, **_kwargs):
        raise URLError("network down")

    monkeypatch.setattr(svc, "urlopen", _raise_url_error)

    tip = svc.fetch_privacy_tip()
    assert tip["fallback"] is True
    assert tip["source"] == "local-fallback"
