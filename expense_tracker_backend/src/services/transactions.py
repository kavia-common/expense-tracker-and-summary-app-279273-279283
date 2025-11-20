from __future__ import annotations

from datetime import date
from typing import Optional, Tuple, List

from sqlalchemy.orm import Session

from src.models.models import Transaction
from src.repositories.transactions import TransactionRepository


class TransactionService:
    """Business logic for transactions."""

    def __init__(self, session: Session) -> None:
        self.repo = TransactionRepository(session)

    def create(
        self,
        user_id: int,
        amount: float,
        currency: str,
        occurred_on: date,
        note: Optional[str],
        category_id: Optional[int],
    ) -> Transaction:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        currency = currency.upper()
        if len(currency) != 3:
            raise ValueError("Currency must be 3-letter code")
        return self.repo.create(user_id, amount, currency, occurred_on, note, category_id)

    def update(
        self,
        user_id: int,
        txn_id: int,
        amount: float,
        currency: str,
        occurred_on: date,
        note: Optional[str],
        category_id: Optional[int],
    ) -> Transaction:
        txn = self.repo.get_owned(user_id, txn_id)
        if not txn:
            raise PermissionError("Transaction not found")
        if amount <= 0:
            raise ValueError("Amount must be positive")
        currency = currency.upper()
        if len(currency) != 3:
            raise ValueError("Currency must be 3-letter code")
        return self.repo.update(txn, amount, currency, occurred_on, note, category_id)

    def delete(self, user_id: int, txn_id: int) -> None:
        txn = self.repo.get_owned(user_id, txn_id)
        if not txn:
            raise PermissionError("Transaction not found")
        self.repo.delete(txn)

    def list(
        self,
        user_id: int,
        limit: int,
        offset: int,
        start_date: Optional[date],
        end_date: Optional[date],
        category_id: Optional[int],
        min_amount: Optional[float],
        max_amount: Optional[float],
        sort: str,
    ) -> Tuple[List[Transaction], int]:
        return self.repo.list_owned(
            user_id, limit, offset, start_date, end_date, category_id, min_amount, max_amount, sort
        )
