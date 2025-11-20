from __future__ import annotations

import logging
from typing import Tuple, Optional

from sqlalchemy.orm import Session

from src.core.auth import create_access_and_refresh_tokens
from src.core.passwords import hash_password, verify_password
from src.repositories.users import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and authorization operations."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def register(self, email: str, password: str, name: Optional[str]) -> int:
        pwd_hash = hash_password(password)
        user = self.users.create(email=email, name=name, password_hash=pwd_hash)
        # Persist hash attached attribute in a lightweight credential store (in-memory for demo)
        # In a production-ready design, credentials should be persisted in DB. For demo, attach to object.
        setattr(user, "_password_hash", pwd_hash)
        return user.id

    def login(self, email: str, password: str) -> Tuple[int, str, str, int, int]:
        user = self.users.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")
        pwd_hash = getattr(user, "_password_hash", None)
        # For demo seed users created via CLI don't have password; allow demo password 'password' if unset
        if pwd_hash is None:
            # set default
            pwd_hash = hash_password("password")
            setattr(user, "_password_hash", pwd_hash)
        if not verify_password(password, pwd_hash):
            raise ValueError("Invalid credentials")
        access, refresh, access_exp, refresh_exp = create_access_and_refresh_tokens(user.id)
        return user.id, access, refresh, access_exp, refresh_exp
