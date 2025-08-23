"""
Deposit model
"""

from sqlalchemy import Column, String, DateTime, Numeric
from app.models.base import BaseModel


class Deposit(BaseModel):
    time = Column(DateTime, nullable=False, index=True)
    currency = Column(String(20), nullable=False, index=True)
    amount = Column(Numeric(38, 18), nullable=False)
    txid = Column(String(200), nullable=True, index=True)
    status = Column(String(30), nullable=True)
