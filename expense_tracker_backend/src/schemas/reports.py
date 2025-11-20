from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    """Date range request body."""
    start_date: date = Field(..., description="Inclusive start date")
    end_date: date = Field(..., description="Inclusive end date")


class CategoryTotal(BaseModel):
    """Category totals response row."""
    category: str = Field(..., description="Category name or 'Uncategorized'")
    total: float = Field(..., description="Total amount")


class DailySpend(BaseModel):
    """Daily spending response row."""
    date: str = Field(..., description="Day in ISO format")
    total: float = Field(..., description="Total amount for the day")


class CategoryTotalsResponse(BaseModel):
    """Wrapper for category totals."""
    results: List[CategoryTotal]


class DailySpendResponse(BaseModel):
    """Wrapper for daily spend."""
    results: List[DailySpend]
