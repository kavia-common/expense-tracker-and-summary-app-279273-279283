from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import secrets
import base64
import hmac
import hashlib
from fastapi import Response, Request

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class TokenError(Exception):
    """Custom exception for token handling errors."""


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(message: bytes, secret: bytes) -> str:
    sig = hmac.new(secret, message, hashlib.sha256).digest()
    return _b64url_encode(sig)


def _secure_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())


def _from_timestamp(ts: int) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _make_token(payload: Dict[str, Any], secret: str, exp_seconds: int) -> str:
    """Create a minimal JWT-like signed token using HMAC-SHA256.
    Header: {"alg":"HS256","typ":"JWT"}
    Payload: user data + "exp" epoch seconds
    """
    header = {"alg": "HS256", "typ": "JWT"}
    exp = _now_utc() + timedelta(seconds=exp_seconds)
    payload = {**payload, "exp": _to_timestamp(exp)}
    header_b64 = _b64url_encode(bytes(__import__("json").dumps(header, separators=(",", ":")).encode("utf-8")))
    payload_b64 = _b64url_encode(bytes(__import__("json").dumps(payload, separators=(",", ":")).encode("utf-8")))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig = _sign(signing_input, secret.encode("utf-8"))
    return f"{header_b64}.{payload_b64}.{sig}"


def _decode_token(token: str, secret: str) -> Dict[str, Any]:
    """Verify token signature and expiration."""
    try:
        header_b64, payload_b64, sig = token.split(".")
    except ValueError as exc:
        raise TokenError("Invalid token format") from exc
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_sig = _sign(signing_input, secret.encode("utf-8"))
    if not _secure_compare(sig, expected_sig):
        raise TokenError("Invalid token signature")
    try:
        payload_json = _b64url_decode(payload_b64).decode("utf-8")
        payload = __import__("json").loads(payload_json)
    except Exception as exc:  # noqa: BLE001
        raise TokenError("Invalid token payload") from exc
    exp_ts = payload.get("exp")
    if not isinstance(exp_ts, int):
        raise TokenError("Invalid token exp")
    if _from_timestamp(exp_ts) < _now_utc():
        raise TokenError("Token expired")
    return payload


# PUBLIC_INTERFACE
def create_access_and_refresh_tokens(user_id: int) -> Tuple[str, str, int, int]:
    """Create access and refresh tokens for a given user_id with configured expirations.

    Returns:
        (access_token, refresh_token, access_expires_seconds, refresh_expires_seconds)
    """
    settings = get_settings()
    if not settings.secret_key:
        # Raise explicit error for missing security configuration
        raise RuntimeError("SECRET_KEY is required for token generation")

    access_seconds = max(settings.access_token_expires_min, 1) * 60
    refresh_seconds = max(settings.refresh_token_expires_days, 1) * 24 * 60 * 60
    # Ensure refresh token has random id to prevent predictability
    jti = _b64url_encode(secrets.token_bytes(16))

    access_payload: Dict[str, Any] = {"sub": str(user_id), "type": "access"}
    refresh_payload: Dict[str, Any] = {"sub": str(user_id), "type": "refresh", "jti": jti}
    access_token = _make_token(access_payload, settings.secret_key, access_seconds)
    refresh_token = _make_token(refresh_payload, settings.secret_key, refresh_seconds)
    return access_token, refresh_token, access_seconds, refresh_seconds


# PUBLIC_INTERFACE
def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify an access token and return payload."""
    settings = get_settings()
    if not settings.secret_key:
        raise RuntimeError("SECRET_KEY is required for token verification")
    payload = _decode_token(token, settings.secret_key)
    if payload.get("type") != "access":
        raise TokenError("Invalid token type")
    return payload


# PUBLIC_INTERFACE
def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Verify a refresh token and return payload."""
    settings = get_settings()
    if not settings.secret_key:
        raise RuntimeError("SECRET_KEY is required for token verification")
    payload = _decode_token(token, settings.secret_key)
    if payload.get("type") != "refresh":
        raise TokenError("Invalid token type")
    return payload


# PUBLIC_INTERFACE
def set_refresh_cookie(response: Response, refresh_token: str, max_age: int) -> None:
    """Set httpOnly secure refresh token cookie."""
    settings = get_settings()
    cookie_secure = settings.cookie_secure
    cookie_samesite = settings.cookie_samesite
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        path="/auth/refresh",
    )


# PUBLIC_INTERFACE
def clear_refresh_cookie(response: Response) -> None:
    """Clear refresh cookie on logout."""
    settings = get_settings()
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path="/auth/refresh",
    )


# PUBLIC_INTERFACE
def get_refresh_cookie(request: Request) -> Optional[str]:
    """Read refresh cookie from request."""
    settings = get_settings()
    return request.cookies.get(settings.refresh_cookie_name)
