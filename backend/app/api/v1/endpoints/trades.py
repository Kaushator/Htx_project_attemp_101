"""
Trades endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from typing import Optional
from datetime import date, datetime
from app.services import db_service

router = APIRouter()


def _dt(d: Optional[date], end=False) -> Optional[datetime]:
    if not d:
        return None
    if end:
        return datetime(d.year, d.month, d.day, 23, 59, 59)
    return datetime(d.year, d.month, d.day, 0, 0, 0)


@router.get("/trades")
async def get_trades(
    symbol: Optional[str] = Query(None, description="Filter by trading symbol"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, le=1000, description="Number of trades to return"),
    offset: int = Query(0, ge=0, description="Number of trades to skip"),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await db_service.get_trades(
        db,
        symbol=symbol,
        start=_dt(start_date),
        end=_dt(end_date, end=True),
        limit=limit,
        offset=offset,
    )
    return {
        "trades": [
            {
                "id": r.id,
                "symbol": r.symbol,
                "time": r.time.isoformat(),
                "side": r.side,
                "quantity": float(r.quantity),
                "price": float(r.price),
                "fee": float(r.fee or 0),
                "fee_currency": r.fee_currency,
                "total": float(r.total or (r.quantity * r.price)),
                "order_id": r.order_id,
                "trade_id": r.trade_id,
            }
            for r in rows
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/trades/summary")
async def get_trades_summary(
    symbol: Optional[str] = Query(None, description="Filter by trading symbol"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await db_service.trades_summary(
        db,
        symbol=symbol,
        start=_dt(start_date),
        end=_dt(end_date, end=True),
    )
