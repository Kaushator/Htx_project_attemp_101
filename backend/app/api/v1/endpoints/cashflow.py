"""
Cashflow endpoints (deposits, withdrawals, transfers)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.db_service import cashflow_sums_by_currency
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()



# Явный обработчик для /cashflow (возвращает summary, как /cashflow/summary)
@router.get("/cashflow")
async def cashflow_root(db: AsyncSession = Depends(get_db)):
    try:
        data = await cashflow_sums_by_currency(db)
        total_deposits = sum(data["deposits"].values())
        total_withdrawals = sum(data["withdrawals"].values())
        net_cashflow = total_deposits - total_withdrawals
        return {
            "by_currency": data,
            "totals": {
                "deposits": total_deposits,
                "withdrawals": total_withdrawals,
                "net_cashflow": net_cashflow,
            },
        }
    except Exception as e:
        logger.error(f"Failed to get cashflow summary: {e}")
        return {
            "by_currency": {},
            "totals": {"deposits": 0, "withdrawals": 0, "net_cashflow": 0},
            "error": str(e)
        }


@router.get("/cashflow/deposits")
async def get_deposits(
    currency: Optional[str] = Query(None, description="Filter by currency"),
    limit: int = Query(100, le=1000, description="Number of deposits to return"),
    offset: int = Query(0, ge=0, description="Number of deposits to skip"),
    db: AsyncSession = Depends(get_db)
):
    """Get deposits with optional filtering"""
    # TODO: Implement deposits retrieval logic
    return {
        "deposits": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/cashflow/withdrawals")
async def get_withdrawals(
    currency: Optional[str] = Query(None, description="Filter by currency"),
    limit: int = Query(100, le=1000, description="Number of withdrawals to return"),
    offset: int = Query(0, ge=0, description="Number of withdrawals to skip"),
    db: AsyncSession = Depends(get_db)
):
    """Get withdrawals with optional filtering"""
    # TODO: Implement withdrawals retrieval logic
    return {
        "withdrawals": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/cashflow/transfers")
async def get_transfers(
    currency: Optional[str] = Query(None, description="Filter by currency"),
    limit: int = Query(100, le=1000, description="Number of transfers to return"),
    offset: int = Query(0, ge=0, description="Number of transfers to skip"),
    db: AsyncSession = Depends(get_db)
):
    """Get transfers with optional filtering"""
    # TODO: Implement transfers retrieval logic
    return {
        "transfers": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/cashflow/summary")
async def get_cashflow_summary(db: AsyncSession = Depends(get_db)):
    data = await cashflow_sums_by_currency(db)
    total_deposits = sum(data["deposits"].values())
    total_withdrawals = sum(data["withdrawals"].values())
    net_cashflow = total_deposits - total_withdrawals
    return {
        "by_currency": data,
        "totals": {
            "deposits": total_deposits,
            "withdrawals": total_withdrawals,
            "net_cashflow": net_cashflow,
        },
    }
