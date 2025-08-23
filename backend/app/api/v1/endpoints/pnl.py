"""
PnL (Profit and Loss) calculation endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from typing import Optional
from datetime import date, datetime
from app.services import pnl as pnl_service

router = APIRouter()


def _dt(d: Optional[date], end=False) -> Optional[datetime]:
    if not d:
        return None
    if end:
        return datetime(d.year, d.month, d.day, 23, 59, 59)
    return datetime(d.year, d.month, d.day, 0, 0, 0)


@router.get("/pnl/summary")
async def get_pnl_summary(
    symbol: Optional[str] = Query(None, description="Filter by trading symbol"),
    start_date: Optional[date] = Query(None, description="Start date for calculation"),
    end_date: Optional[date] = Query(None, description="End date for calculation"),
    db: AsyncSession = Depends(get_db)
):
    return await pnl_service.pnl_summary(db, symbol, _dt(start_date), _dt(end_date, end=True))


@router.get("/pnl/daily")
async def get_daily_pnl(
    symbol: Optional[str] = Query(None, description="Filter by trading symbol"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db)
):
    items = await pnl_service.pnl_daily(db, symbol, _dt(start_date), _dt(end_date, end=True))
    return {"total": len(items), "daily_pnl": items}


@router.get("/pnl/drawdown")
async def get_drawdown_analysis(
    symbol: Optional[str] = Query(None, description="Filter by trading symbol"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db)
):
    return await pnl_service.pnl_drawdown(db, symbol, _dt(start_date), _dt(end_date, end=True))
