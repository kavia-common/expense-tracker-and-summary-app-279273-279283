from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Create category request."""
    name: str = Field(..., min_length=1, max_length=64)


class CategoryUpdate(BaseModel):
    """Update category request."""
    name: str = Field(..., min_length=1, max_length=64)


class CategoryOut(BaseModel):
    """Category response."""
    id: int
    name: str

    class Config:
        from_attributes = True
