from __future__ import annotations

from datetime import date
from typing import List, Dict

from sqlalchemy.orm import Session

from src.repositories.reports import ReportRepository


class ReportService:
    """Reporting operations."""

    def __init__(self, session: Session) -> None:
        self.repo = ReportRepository(session)

    def totals_by_category(self, user_id: int, start: date, end: date) -> List[Dict[str, object]]:
        return self.repo.totals_by_category(user_id, start, end)

    def daily_spend(self, user_id: int, start: date, end: date) -> List[Dict[str, object]]:
        return self.repo.daily_spend(user_id, start, end)
