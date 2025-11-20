from __future__ import annotations

from typing import Optional, Tuple, List

from sqlalchemy.orm import Session

from src.models.models import Category
from src.repositories.categories import CategoryRepository


class CategoryService:
    """Business logic for categories."""

    def __init__(self, session: Session) -> None:
        self.repo = CategoryRepository(session)

    def create(self, user_id: int, name: str) -> Category:
        name = name.strip()
        if not name:
            raise ValueError("Category name required")
        return self.repo.create(user_id, name)

    def update(self, user_id: int, category_id: int, name: str) -> Category:
        cat = self.repo.get_owned(user_id, category_id)
        if not cat:
            raise PermissionError("Category not found")
        name = name.strip()
        if not name:
            raise ValueError("Category name required")
        return self.repo.update(cat, name)

    def delete(self, user_id: int, category_id: int) -> None:
        cat = self.repo.get_owned(user_id, category_id)
        if not cat:
            raise PermissionError("Category not found")
        self.repo.delete(cat)

    def list(self, user_id: int, limit: int, offset: int, q: Optional[str]) -> Tuple[List[Category], int]:
        return self.repo.list_owned(user_id, limit, offset, q)
