"""Declarative base and common model mixins."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import DateTime, Integer


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize model to a dictionary (basic fields only)."""
        data: Dict[str, Any] = {}
        for col in self.__table__.columns:  # type: ignore[attr-defined]
            data[col.name] = getattr(self, col.name)
        return data


class TimestampMixin:
    """Add created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class PKMixin:
    """Primary key id column."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)


class TableNameMixin:
    """Automatic snake_case table names from class name."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        return "".join(
            ["_" + c.lower() if c.isupper() else c for c in cls.__name__]
        ).lstrip("_")
