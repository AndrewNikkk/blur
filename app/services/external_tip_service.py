import json
import logging
import threading
import time
from collections import deque
from datetime import datetime
from typing import Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


logger = logging.getLogger(__name__)

_rate_lock = threading.Lock()
_request_timestamps = deque()
_cache_lock = threading.Lock()
_cached_tip: Optional[Dict[str, object]] = None
_cached_at: Optional[float] = None


def _fallback_tip() -> Dict[str, object]:
    return {
        "title": "Локальный совет по безопасности",
        "content": "Перед публикацией документов проверяйте, что персональные данные скрыты.",
        "source": "local-fallback",
        "fetched_at": datetime.now(),
        "fallback": True,
    }


def _enforce_rate_limit() -> None:
    now = time.time()
    window_start = now - 60
    with _rate_lock:
        while _request_timestamps and _request_timestamps[0] < window_start:
            _request_timestamps.popleft()
        if len(_request_timestamps) >= settings.EXTERNAL_TIP_RATE_LIMIT_PER_MIN:
            raise RuntimeError("Rate limit exceeded for external API")
        _request_timestamps.append(now)


def _load_from_cache() -> Optional[Dict[str, object]]:
    with _cache_lock:
        if _cached_tip is None or _cached_at is None:
            return None
        if (time.time() - _cached_at) > settings.EXTERNAL_TIP_CACHE_TTL_SEC:
            return None
        return dict(_cached_tip)


def _save_to_cache(tip: Dict[str, object]) -> None:
    global _cached_tip, _cached_at
    with _cache_lock:
        _cached_tip = dict(tip)
        _cached_at = time.time()


def fetch_privacy_tip() -> Dict[str, object]:
    cached = _load_from_cache()
    if cached:
        return cached

    if not settings.EXTERNAL_TIP_API_KEY:
        logger.warning("EXTERNAL_TIP_API_KEY is missing, returning fallback tip")
        fallback = _fallback_tip()
        _save_to_cache(fallback)
        return fallback

    _enforce_rate_limit()

    headers = {"X-Api-Key": settings.EXTERNAL_TIP_API_KEY}
    request = Request(settings.EXTERNAL_TIP_API_URL, headers=headers, method="GET")

    for attempt in range(settings.EXTERNAL_TIP_MAX_RETRIES + 1):
        try:
            with urlopen(request, timeout=settings.EXTERNAL_TIP_TIMEOUT_SEC) as response:
                payload = json.loads(response.read().decode("utf-8"))
            fact_text = ""
            if isinstance(payload, list) and payload:
                fact_text = str(payload[0].get("fact", "")).strip()
            elif isinstance(payload, dict):
                fact_text = str(payload.get("fact", "")).strip()

            if not fact_text:
                raise ValueError("External API returned empty fact")

            normalized = {
                "title": "Совет из внешнего API",
                "content": fact_text,
                "source": "api-ninjas",
                "fetched_at": datetime.now(),
                "fallback": False,
            }
            _save_to_cache(normalized)
            return normalized
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            logger.warning("External tip fetch failed on attempt %s: %s", attempt + 1, exc)
            if attempt < settings.EXTERNAL_TIP_MAX_RETRIES:
                time.sleep(0.25 * (attempt + 1))
                continue
            fallback = _fallback_tip()
            _save_to_cache(fallback)
            return fallback

    fallback = _fallback_tip()
    _save_to_cache(fallback)
    return fallback
