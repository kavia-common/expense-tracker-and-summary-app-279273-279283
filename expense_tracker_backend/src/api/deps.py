from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session

from src.core.auth import verify_access_token, TokenError, get_refresh_cookie, verify_refresh_token
from src.db.session import get_db
from src.repositories.users import UserRepository

logger = logging.getLogger(__name__)


# PUBLIC_INTERFACE
def get_db_dep() -> Session:  # type: ignore[override]
    """FastAPI dependency to provide a DB session."""
    for db in get_db():
        return db  # pragma: no cover
    raise RuntimeError("DB dependency failed")


# PUBLIC_INTERFACE
def get_current_user_id(
    authorization: Optional[str] = Header(default=None),
) -> int:
    """Extract and validate Bearer access token and return current user id."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = verify_access_token(token)
    except TokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")  # noqa: B904
    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    return user_id


# PUBLIC_INTERFACE
def get_user_repo(db: Session = Depends(get_db_dep)) -> UserRepository:
    """Provide UserRepository instance."""
    return UserRepository(db)


# PUBLIC_INTERFACE
def get_refresh_token_from_cookie(request: Request) -> str:
    """Read and validate refresh token from httpOnly cookie."""
    token = get_refresh_cookie(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        verify_refresh_token(token)
    except TokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")  # noqa: B904
    return token
