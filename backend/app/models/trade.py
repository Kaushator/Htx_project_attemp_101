"""
Trade model
"""

from sqlalchemy import Column, String, DateTime, Numeric
from app.models.base import BaseModel


class Trade(BaseModel):
    symbol = Column(String(50), index=True, nullable=False)
    time = Column(DateTime, nullable=False, index=True)
    side = Column(String(4), nullable=False)  # buy/sell
    quantity = Column(Numeric(38, 18), nullable=False)
    price = Column(Numeric(38, 18), nullable=False)
    fee = Column(Numeric(38, 18), nullable=True)
    fee_currency = Column(String(20), nullable=True)
    total = Column(Numeric(38, 18), nullable=True)
    order_id = Column(String(100), nullable=True, index=True)
    trade_id = Column(String(100), nullable=True, index=True)
