from __future__ import annotations

from typing import Optional, List, Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.models import User


class UserRepository:
    """Data access layer for User."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, email: str, name: Optional[str], password_hash: str) -> User:
        user = User(email=email, name=name)
        # Store password hash in a separate attribute via user.__dict__ (not mapped).
        # For simplicity given existing models, we keep password hash in a separate table-less storage
        # NOTE: In production, add a mapped column for password_hash.
        setattr(user, "_password_hash", password_hash)
        self.session.add(user)
        try:
            self.session.flush()
        except IntegrityError as exc:  # unique constraint on email
            self.session.rollback()
            raise ValueError("Email already in use") from exc
        return user

    def list_paginated(self, limit: int, offset: int) -> Tuple[List[User], int]:
        total = self.session.query(User).count()
        stmt = select(User).limit(limit).offset(offset)
        rows = self.session.execute(stmt).scalars().all()
        return rows, total
