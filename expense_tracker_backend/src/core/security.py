"""Security helpers: password hashing, token utilities (placeholder for future work)."""
from __future__ import annotations

import hashlib
from typing import Final


# Not storing plaintext secrets; provide safe one-way hashing for future use.
_SALT_PREFIX: Final[str] = "expensetracker::"


# PUBLIC_INTERFACE
def sha256_hash(value: str) -> str:
    """Return a salted SHA-256 hash for the provided string."""
    h = hashlib.sha256()
    h.update((_SALT_PREFIX + value).encode("utf-8"))
    return h.hexdigest()
