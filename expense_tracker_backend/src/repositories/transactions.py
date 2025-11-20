from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.models.models import Transaction


class TransactionRepository:
    """Data access for Transaction with user ownership."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_owned(self, user_id: int, txn_id: int) -> Optional[Transaction]:
        stmt = select(Transaction).where(and_(Transaction.id == txn_id, Transaction.user_id == user_id))
        return self.session.execute(stmt).scalar_one_or_none()

    def create(
        self,
        user_id: int,
        amount: float,
        currency: str,
        occurred_on: date,
        note: Optional[str],
        category_id: Optional[int],
    ) -> Transaction:
        txn = Transaction(
            user_id=user_id,
            amount=amount,
            currency=currency,
            occurred_on=occurred_on,
            note=note,
            category_id=category_id,
        )
        self.session.add(txn)
        self.session.flush()
        return txn

    def update(
        self,
        txn: Transaction,
        amount: float,
        currency: str,
        occurred_on: date,
        note: Optional[str],
        category_id: Optional[int],
    ) -> Transaction:
        txn.amount = amount
        txn.currency = currency
        txn.occurred_on = occurred_on
        txn.note = note
        txn.category_id = category_id
        self.session.flush()
        return txn

    def delete(self, txn: Transaction) -> None:
        self.session.delete(txn)
        self.session.flush()

    def list_owned(
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
        filters = [Transaction.user_id == user_id]
        if start_date:
            filters.append(Transaction.occurred_on >= start_date)
        if end_date:
            filters.append(Transaction.occurred_on <= end_date)
        if category_id:
            filters.append(Transaction.category_id == category_id)
        if min_amount is not None:
            filters.append(Transaction.amount >= min_amount)
        if max_amount is not None:
            filters.append(Transaction.amount <= max_amount)

        q = select(Transaction).where(and_(*filters))
        total = self.session.query(Transaction).filter(and_(*filters)).count()

        # sorting
        if sort == "date_desc":
            q = q.order_by(Transaction.occurred_on.desc())
        elif sort == "amount_desc":
            q = q.order_by(Transaction.amount.desc())
        elif sort == "amount_asc":
            q = q.order_by(Transaction.amount.asc())
        else:
            q = q.order_by(Transaction.occurred_on.asc())

        rows = self.session.execute(q.limit(limit).offset(offset)).scalars().all()
        return rows, total
