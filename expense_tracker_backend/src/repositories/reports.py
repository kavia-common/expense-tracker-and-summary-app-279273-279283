from __future__ import annotations

from datetime import date
from typing import List, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.models import Transaction, Category


class ReportRepository:
    """Aggregated reporting queries."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def totals_by_category(self, user_id: int, start_date: date, end_date: date) -> List[Dict[str, object]]:
        q = (
            self.session.query(Category.name, func.sum(Transaction.amount).label("total"))
            .join(Category, Category.id == Transaction.category_id, isouter=True)
            .filter(Transaction.user_id == user_id)
            .filter(Transaction.occurred_on >= start_date, Transaction.occurred_on <= end_date)
            .group_by(Category.name)
            .order_by(func.sum(Transaction.amount).desc())
        )
        result = [{"category": name if name is not None else "Uncategorized", "total": float(total or 0)} for name, total in q]
        return result

    def daily_spend(self, user_id: int, start_date: date, end_date: date) -> List[Dict[str, object]]:
        q = (
            self.session.query(Transaction.occurred_on, func.sum(Transaction.amount).label("total"))
            .filter(Transaction.user_id == user_id)
            .filter(Transaction.occurred_on >= start_date, Transaction.occurred_on <= end_date)
            .group_by(Transaction.occurred_on)
            .order_by(Transaction.occurred_on.asc())
        )
        return [{"date": d.isoformat(), "total": float(t or 0)} for d, t in q]
