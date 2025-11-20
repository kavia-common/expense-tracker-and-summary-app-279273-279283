from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, Field, field_validator


class TransactionCreate(BaseModel):
    """Create transaction request."""
    amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    occurred_on: date = Field(...)
    note: str | None = Field(default=None, max_length=255)
    category_id: int | None = Field(default=None)

    @field_validator("currency")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper()


class TransactionUpdate(BaseModel):
    """Update transaction request."""
    amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    occurred_on: date = Field(...)
    note: str | None = Field(default=None, max_length=255)
    category_id: int | None = Field(default=None)

    @field_validator("currency")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper()


class TransactionOut(BaseModel):
    """Transaction response."""
    id: int
    amount: float
    currency: str
    occurred_on: date
    note: str | None
    category_id: int | None

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Standard pagination wrapper."""
    items: List[TransactionOut]
    total: int
    limit: int
    offset: int
