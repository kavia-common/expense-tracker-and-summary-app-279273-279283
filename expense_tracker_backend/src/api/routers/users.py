from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user_id, get_db_dep
from src.schemas.users import UserOut
from src.repositories.users import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Get current user profile",
    response_model=UserOut,
)
def me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_dep)) -> UserOut:
    """Return the profile of the authenticated user."""
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(user)
