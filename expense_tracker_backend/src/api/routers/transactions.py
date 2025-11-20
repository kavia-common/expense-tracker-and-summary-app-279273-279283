from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session

from src.api.deps import get_current_user_id, get_db_dep
from src.schemas.transactions import TransactionCreate, TransactionUpdate, TransactionOut, PaginatedResponse
from src.services.transactions import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    summary="Create transaction",
    response_model=TransactionOut,
    status_code=201,
)
def create_transaction(
    payload: TransactionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
) -> TransactionOut:
    """Create a transaction for the authenticated user."""
    svc = TransactionService(db)
    try:
        txn = svc.create(
            user_id=user_id,
            amount=payload.amount,
            currency=payload.currency,
            occurred_on=payload.occurred_on,
            note=payload.note,
            category_id=payload.category_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))  # noqa: B904
    return TransactionOut.model_validate(txn)


@router.get(
    "",
    summary="List transactions with filtering and pagination",
    response_model=PaginatedResponse,
)
def list_transactions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    min_amount: Optional[float] = Query(default=None, ge=0),
    max_amount: Optional[float] = Query(default=None, ge=0),
    sort: str = Query(default="date_desc", pattern="^(date_(asc|desc)|amount_(asc|desc))$"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
) -> PaginatedResponse:
    """List transactions with date/amount/category filters and sorting."""
    svc = TransactionService(db)
    items, total = svc.list(
        user_id=user_id,
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        min_amount=min_amount,
        max_amount=max_amount,
        sort=sort,
    )
    return PaginatedResponse(
        items=[TransactionOut.model_validate(t) for t in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.put(
    "/{transaction_id}",
    summary="Update transaction",
    response_model=TransactionOut,
)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
) -> TransactionOut:
    """Update a transaction."""
    svc = TransactionService(db)
    try:
        txn = svc.update(
            user_id=user_id,
            txn_id=transaction_id,
            amount=payload.amount,
            currency=payload.currency,
            occurred_on=payload.occurred_on,
            note=payload.note,
            category_id=payload.category_id,
        )
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")  # noqa: B904
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))  # noqa: B904
    return TransactionOut.model_validate(txn)


@router.delete(
    "/{transaction_id}",
    summary="Delete transaction",
    status_code=204,
)
def delete_transaction(
    transaction_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
):
    """Delete a transaction and return 204 No Content."""
    svc = TransactionService(db)
    try:
        svc.delete(user_id, transaction_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")  # noqa: B904
    return Response(status_code=status.HTTP_204_NO_CONTENT)
