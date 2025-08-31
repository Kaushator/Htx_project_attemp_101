"""
DB service: CRUD and aggregate queries
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.trade import Trade
from app.models.deposit import Deposit
from app.models.withdraw import Withdraw
from app.models.transfer import Transfer


# Trades
async def create_trades(db: AsyncSession, trades: List[Dict[str, Any]]) -> int:
    objs = [Trade(**t) for t in trades]
    db.add_all(objs)
    await db.flush()
    await db.commit()
    return len(objs)


async def get_trades(
    db: AsyncSession,
    symbol: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> Tuple[List[Trade], int]:
    stmt = select(Trade)
    cnt = select(func.count(Trade.id))
    if symbol:
        stmt = stmt.where(Trade.symbol == symbol)
        cnt = cnt.where(Trade.symbol == symbol)
    if start:
        stmt = stmt.where(Trade.time >= start)
        cnt = cnt.where(Trade.time >= start)
    if end:
        stmt = stmt.where(Trade.time <= end)
        cnt = cnt.where(Trade.time <= end)
    total = (await db.execute(cnt)).scalar_one()
    rows = (
        (await db.execute(stmt.order_by(desc(Trade.time)).limit(limit).offset(offset)))
        .scalars()
        .all()
    )
    return rows, total


async def trades_summary(
    db: AsyncSession,
    symbol: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Dict[str, Any]:
    stmt = select(
        func.count(Trade.id),
        func.sum(func.abs(Trade.quantity)),
        func.sum(Trade.quantity * Trade.price),
    )
    if symbol:
        stmt = stmt.where(Trade.symbol == symbol)
    if start:
        stmt = stmt.where(Trade.time >= start)
    if end:
        stmt = stmt.where(Trade.time <= end)
    res = (await db.execute(stmt)).first()
    return {
        "total_trades": int(res[0] or 0),
        "total_volume": float(res[1] or 0),
        "gross_amount": float(res[2] or 0),
    }


# Cashflow summaries
async def cashflow_sums_by_currency(db: AsyncSession) -> Dict[str, Any]:
    dep = (
        await db.execute(
            select(Deposit.currency, func.sum(Deposit.amount)).group_by(
                Deposit.currency
            )
        )
    ).all()
    wdr = (
        await db.execute(
            select(Withdraw.currency, func.sum(Withdraw.amount)).group_by(
                Withdraw.currency
            )
        )
    ).all()
    trn = (
        await db.execute(
            select(Transfer.currency, func.sum(Transfer.amount)).group_by(
                Transfer.currency
            )
        )
    ).all()
    return {
        "deposits": {c: float(a or 0) for c, a in dep},
        "withdrawals": {c: float(a or 0) for c, a in wdr},
        "transfers": {c: float(a or 0) for c, a in trn},
    }


# Bulk create methods
async def create_deposits(db: AsyncSession, deposits: List[Dict[str, Any]]) -> int:
    objs = [Deposit(**d) for d in deposits]
    db.add_all(objs)
    await db.flush()
    await db.commit()
    return len(objs)


async def create_withdrawals(
    db: AsyncSession, withdrawals: List[Dict[str, Any]]
) -> int:
    objs = [Withdraw(**w) for w in withdrawals]
    db.add_all(objs)
    await db.flush()
    await db.commit()
    return len(objs)


async def create_transfers(db: AsyncSession, transfers: List[Dict[str, Any]]) -> int:
    objs = [Transfer(**t) for t in transfers]
    db.add_all(objs)
    await db.flush()
    await db.commit()
    return len(objs)
