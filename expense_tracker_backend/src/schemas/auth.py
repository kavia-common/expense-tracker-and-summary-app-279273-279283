from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    """Access token response model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type, typically 'bearer'")
    expires_in: int = Field(..., description="Seconds until access token expiration")


class RegisterRequest(BaseModel):
    """Registration request payload."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, max_length=128, description="Strong password")
    name: str | None = Field(default=None, description="Display name")


class LoginRequest(BaseModel):
    """Login request payload."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
