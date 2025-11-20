from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    """User response model."""
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    name: str | None = Field(default=None, description="Display name")

    class Config:
        from_attributes = True
