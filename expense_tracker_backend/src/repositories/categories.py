from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.models import Category


class CategoryRepository:
    """Data access for Category with user ownership enforcement."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_owned(self, user_id: int, category_id: int) -> Optional[Category]:
        stmt = select(Category).where(and_(Category.id == category_id, Category.user_id == user_id))
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, user_id: int, name: str) -> Category:
        category = Category(user_id=user_id, name=name)
        self.session.add(category)
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("Category name must be unique per user") from exc
        return category

    def update(self, category: Category, name: str) -> Category:
        category.name = name
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("Category name must be unique per user") from exc
        return category

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.flush()

    def list_owned(self, user_id: int, limit: int, offset: int, q: Optional[str]) -> Tuple[List[Category], int]:
        base = select(Category).where(Category.user_id == user_id)
        count_q = self.session.query(Category).filter(Category.user_id == user_id)
        if q:
            like = f"%{q.strip()}%"
            base = base.where(Category.name.ilike(like))
            count_q = count_q.filter(Category.name.ilike(like))
        total = count_q.count()
        rows = self.session.execute(base.order_by(Category.name.asc()).limit(limit).offset(offset)).scalars().all()
        return rows, total
