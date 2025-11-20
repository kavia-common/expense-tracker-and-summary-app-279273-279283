from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user_id, get_db_dep
from src.schemas.reports import CategoryTotalsResponse, DailySpendResponse, CategoryTotal, DailySpend
from src.services.reports import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/category-totals",
    summary="Totals by category within date range",
    response_model=CategoryTotalsResponse,
)
def category_totals(
    start_date: date = Query(..., description="Start date inclusive"),
    end_date: date = Query(..., description="End date inclusive"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
) -> CategoryTotalsResponse:
    """Aggregate totals grouped by category."""
    if end_date < start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be >= start_date")
    svc = ReportService(db)
    rows = svc.totals_by_category(user_id, start_date, end_date)
    return CategoryTotalsResponse(results=[CategoryTotal(**r) for r in rows])


@router.get(
    "/daily-spend",
    summary="Daily spend over date range",
    response_model=DailySpendResponse,
)
def daily_spend(
    start_date: date = Query(..., description="Start date inclusive"),
    end_date: date = Query(..., description="End date inclusive"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_dep),
) -> DailySpendResponse:
    """Daily spend totals per day."""
    if end_date < start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be >= start_date")
    svc = ReportService(db)
    rows = svc.daily_spend(user_id, start_date, end_date)
    return DailySpendResponse(results=[DailySpend(**r) for r in rows])
