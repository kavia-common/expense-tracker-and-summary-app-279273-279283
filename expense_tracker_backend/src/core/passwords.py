from __future__ import annotations

import base64
import hashlib
import hmac
import os



_PBKDF2_ALGO = "pbkdf2_sha256"
_ITERATIONS = 390000  # Strong default similar to Django 4.x
_SALT_BYTES = 16
_KEY_LEN = 32


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Generate a PBKDF2-SHA256 password hash.

    Returns:
        Encoded hash string containing algorithm, iterations, salt, and key.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string")
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS, dklen=_KEY_LEN)
    enc_salt = base64.b64encode(salt).decode("ascii")
    enc_key = base64.b64encode(dk).decode("ascii")
    return f"{_PBKDF2_ALGO}${_ITERATIONS}${enc_salt}${enc_key}"


# PUBLIC_INTERFACE
def verify_password(password: str, encoded: str) -> bool:
    """Verify a password against an encoded PBKDF2-SHA256 hash."""
    try:
        algo, iter_s, enc_salt, enc_key = encoded.split("$")
        if algo != _PBKDF2_ALGO:
            return False
        iterations = int(iter_s)
        salt = base64.b64decode(enc_salt.encode("ascii"))
        expected_key = base64.b64decode(enc_key.encode("ascii"))
        test_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=len(expected_key))
        return hmac.compare_digest(test_key, expected_key)
    except Exception:  # noqa: BLE001
        return False
