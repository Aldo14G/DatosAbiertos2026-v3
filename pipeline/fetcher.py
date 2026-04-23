"""pipeline/fetcher.py — Robust HTTP fetcher with SSRF protection.

Features:
- URL validation against SSRF (allowlist + loopback/reject checks)
- Retry logic with exponential backoff (Jittered)
- Timeout handling (connect + read)
- Rate-limit awareness (Retry-After header)
- Snapshot system with timestamps
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import random
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import requests

# ── Allowlist ──────────────────────────────────────────────────
ALLOWED_DOMAINS: frozenset[str] = frozenset({
    "catalogodatos.nl.gob.mx",
    "datos.nl.gob.mx",
    "nl.gob.mx",
})

# Defaults
MAX_RETRIES: int = 3
BASE_DELAY: float = 1.0
MAX_DELAY: float = 30.0
CONNECT_TIMEOUT: int = 10
READ_TIMEOUT: int = 60
SNAPSHOT_DIR: str = "snapshots"
USER_AGENT: str = "DatosAbiertosNL-Fetcher/3.0"


# ── URL Validation ─────────────────────────────────────────────

def _is_loopback_or_local(hostname: str) -> bool:
    """Reject loopback, link-local, and private ranges."""
    lower = hostname.lower()
    return any(
        lower.startswith(prefix)
        for prefix in (
            "localhost", "127.", "10.", "192.168.",
            "172.16.", "172.17.", "172.18.", "172.19.",
            "172.20.", "172.21.", "172.22.", "172.23.",
            "172.24.", "172.25.", "172.26.", "172.27.",
            "172.28.", "172.29.", "172.30.", "172.31.",
            "0.", "::1", "fe80:", "fc00:", "fd00:",
            "169.254.",
        )
    )


def validate_url(url: str) -> bool:
    """Validate URL against SSRF: scheme, domain allowlist, no loopback."""
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    hostname = parsed.hostname or ""
    if _is_loopback_or_local(hostname):
        return False

    return any(hostname.endswith(d) for d in ALLOWED_DOMAINS)


# ── Retry with Exponential Backoff + Jitter ────────────────────

def _sleep_with_jitter(attempt: int) -> None:
    """Exponential backoff with full jitter."""
    cap = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
    delay = random.uniform(0, cap)
    time.sleep(delay)


# ── Core Fetch ─────────────────────────────────────────────────

def fetch_with_retry(
    url: str,
    max_retries: int = MAX_RETRIES,
    method: str = "GET",
    **kwargs,
) -> Optional[requests.Response]:
    """Fetch a URL with retry, backoff, timeout, and rate-limit awareness.

    Args:
        url: Target URL (must pass validate_url).
        max_retries: Number of retry attempts after the first failure.
        method: HTTP method (GET, HEAD, etc.).
        **kwargs: Extra arguments forwarded to requests.request().

    Returns:
        Response object on success, None on permanent failure.
    """
    if not validate_url(url):
        print(f"[fetcher] URL rechazada (SSRF): {url}")
        return None

    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)

    timeout = kwargs.pop("timeout", (CONNECT_TIMEOUT, READ_TIMEOUT))

    for attempt in range(max_retries + 1):
        try:
            resp = requests.request(
                method, url, headers=headers, timeout=timeout, **kwargs,
            )

            # Rate-limit awareness
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                if retry_after is not None:
                    try:
                        wait = float(retry_after)
                    except ValueError:
                        wait = BASE_DELAY * (2 ** attempt)
                    wait = min(wait, MAX_DELAY)
                    print(f"[fetcher] Rate-limited — esperando {wait:.1f}s")
                    time.sleep(wait)
                    continue

            resp.raise_for_status()
            return resp

        except requests.exceptions.Timeout:
            print(f"[fetcher] Timeout (intento {attempt + 1}/{max_retries + 1}): {url}")
        except requests.exceptions.ConnectionError as exc:
            print(f"[fetcher] ConnectionError (intento {attempt + 1}/{max_retries + 1}): {exc}")
        except requests.exceptions.HTTPError as exc:
            print(f"[fetcher] HTTPError (intento {attempt + 1}/{max_retries + 1}): {exc}")
            if 400 <= resp.status_code < 500:
                return None  # Client errors are not retried

        if attempt < max_retries:
            _sleep_with_jitter(attempt)

    print(f"[fetcher] Agotados {max_retries + 1} intentos para: {url}")
    return None


# ── Snapshot System ────────────────────────────────────────────

def save_snapshot(data: dict, prefix: str = "quality") -> str:
    """Save a JSON snapshot with timestamped filename.

    Args:
        data: Serializable dict to persist.
        prefix: Filename prefix (e.g. 'quality', 'advanced').

    Returns:
        Absolute path of the written file.
    """
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{prefix}_{ts}.json"
    path = os.path.join(SNAPSHOT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[fetcher] Snapshot guardado: {path}")
    return os.path.abspath(path)


def load_latest_snapshot(prefix: str = "quality") -> Optional[dict]:
    """Load the most recent snapshot matching the prefix.

    Args:
        prefix: Filename prefix used during save.

    Returns:
        Parsed JSON dict, or None if no snapshots exist.
    """
    if not os.path.isdir(SNAPSHOT_DIR):
        return None

    files = sorted(
        f for f in os.listdir(SNAPSHOT_DIR)
        if f.startswith(prefix) and f.endswith(".json")
    )
    if not files:
        return None

    path = os.path.join(SNAPSHOT_DIR, files[-1])
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def content_hash(data: bytes) -> str:
    """SHA-256 hex digest for content integrity tracking."""
    return hashlib.sha256(data).hexdigest()
