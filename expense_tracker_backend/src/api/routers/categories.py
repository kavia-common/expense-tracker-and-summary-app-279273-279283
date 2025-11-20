from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session

from src.api.deps import get_current_user_id, get_db_dep
from src.schemas.categories import CategoryCreate, CategoryUpdate, CategoryOut
from src.services.categories import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    summary="Create category",
    response_model=CategoryOut,
    status_code=201,
)
def create_category(
    payload: CategoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
) -> CategoryOut:
    """Create a new category for the authenticated user."""
    svc = CategoryService(db)
    try:
        cat = svc.create(user_id, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))  # noqa: B904
    return CategoryOut.model_validate(cat)


@router.get(
    "",
    summary="List categories",
    response_model=list[CategoryOut],
)
def list_categories(
    q: Optional[str] = Query(default=None, description="Search term"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
) -> list[CategoryOut]:
    """List categories owned by the current user with optional search and pagination."""
    svc = CategoryService(db)
    cats, _ = svc.list(user_id, limit, offset, q)
    return [CategoryOut.model_validate(c) for c in cats]


@router.put(
    "/{category_id}",
    summary="Update category",
    response_model=CategoryOut,
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
) -> CategoryOut:
    """Update a category name."""
    svc = CategoryService(db)
    try:
        cat = svc.update(user_id, category_id, payload.name)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")  # noqa: B904
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))  # noqa: B904
    return CategoryOut.model_validate(cat)


@router.delete(
    "/{category_id}",
    summary="Delete category",
    status_code=204,
)
def delete_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
):
    """Delete a category and return 204 No Content."""
    svc = CategoryService(db)
    try:
        svc.delete(user_id, category_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")  # noqa: B904
    return Response(status_code=status.HTTP_204_NO_CONTENT)
