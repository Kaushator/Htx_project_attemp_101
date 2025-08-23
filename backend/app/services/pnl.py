"""
PnL (Profit and Loss) calculation service
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from collections import defaultdict, deque
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.trade import Trade

logger = logging.getLogger(__name__)


def _to_decimal(v) -> Decimal:
    return Decimal(str(v)) if v is not None else Decimal("0")


def _fifo_realized_pnl(trades: List[Trade]) -> Tuple[Decimal, Dict[str, Dict[str, Decimal]], Dict[date, Decimal]]:
    positions: Dict[str, deque] = defaultdict(deque)
    realized = Decimal("0")
    daily: Dict[date, Decimal] = defaultdict(Decimal)
    last_price: Dict[str, Decimal] = {}

    for t in sorted(trades, key=lambda x: x.time):
        sym = t.symbol
        qty = _to_decimal(t.quantity)
        price = _to_decimal(t.price)
        side = (t.side or "").lower()
        notional = qty * price
        last_price[sym] = price
        d = t.time.date()
        if side == "buy":
            positions[sym].append([qty, price])
            daily[d] += -notional
        else:
            remaining = qty
            daily[d] += notional
            while remaining > 0 and positions[sym]:
                lot_qty, lot_price = positions[sym][0]
                consume = min(remaining, lot_qty)
                realized += (price - lot_price) * consume
                lot_qty -= consume
                remaining -= consume
                if lot_qty == 0:
                    positions[sym].popleft()
                else:
                    positions[sym][0][0] = lot_qty
            if remaining > 0:
                positions[sym].appendleft([-remaining, price])

    inventory: Dict[str, Dict[str, Decimal]] = {}
    for sym, lots in positions.items():
        pos_qty = sum(q for q, _ in lots)
        avg_cost = (sum(q * p for q, p in lots) / pos_qty) if pos_qty != 0 else Decimal("0")
        inventory[sym] = {
            "qty": pos_qty,
            "avg_cost": avg_cost,
            "last_price": last_price.get(sym, avg_cost),
        }
    return realized, inventory, daily


async def pnl_summary(
    db: AsyncSession,
    symbol: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Dict[str, Any]:
    stmt = select(Trade)
    if symbol:
        stmt = stmt.where(Trade.symbol == symbol)
    if start:
        stmt = stmt.where(Trade.time >= start)
    if end:
        stmt = stmt.where(Trade.time <= end)
    rows = (await db.execute(stmt)).scalars().all()

    realized, inventory, daily = _fifo_realized_pnl(rows)
    unrealized = Decimal("0")
    total_fees = _to_decimal(sum([_to_decimal(t.fee) for t in rows]))
    for sym, inv in inventory.items():
        qty = inv["qty"]
        if qty == 0:
            continue
        unrealized += (inv["last_price"] - inv["avg_cost"]) * qty

    net = realized + unrealized - total_fees
    return {
        "realized_pnl": float(realized),
        "unrealized_pnl": float(unrealized),
        "total_fees": float(total_fees),
        "net_pnl": float(net),
        "open_positions": {
            sym: {k: float(v) for k, v in inv.items()} for sym, inv in inventory.items()
        },
    }


async def pnl_daily(
    db: AsyncSession,
    symbol: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    stmt = select(Trade)
    if symbol:
        stmt = stmt.where(Trade.symbol == symbol)
    if start:
        stmt = stmt.where(Trade.time >= start)
    if end:
        stmt = stmt.where(Trade.time <= end)
    rows = (await db.execute(stmt)).scalars().all()

    _, _, daily = _fifo_realized_pnl(rows)
    items = [
        {"date": d.isoformat(), "realized_pnl": float(v)} for d, v in sorted(daily.items())
    ]
    return items


async def pnl_drawdown(
    db: AsyncSession,
    symbol: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Dict[str, Any]:
    daily = await pnl_daily(db, symbol, start, end)
    equity = []
    cum = Decimal("0")
    for row in daily:
        cum += _to_decimal(row["realized_pnl"])
        equity.append((row["date"], Decimal(cum)))

    peak = Decimal("-1e100")
    max_dd = Decimal("0")
    max_dd_pct = Decimal("0")
    cur_dd = Decimal("0")

    for dt, eq in equity:
        if eq > peak:
            peak = eq
        dd = peak - eq
        if dd > max_dd:
            max_dd = dd
            max_dd_pct = (dd / peak) if peak != 0 else Decimal("0")
        cur_dd = dd

    return {
        "max_drawdown": float(max_dd),
        "max_drawdown_pct": float(max_dd_pct),
        "current_drawdown": float(cur_dd),
        "points": [{"date": dt, "equity": float(eq)} for dt, eq in equity],
    }
