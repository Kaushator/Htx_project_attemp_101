"""
Transfer model
"""

from sqlalchemy import Column, String, DateTime, Numeric
from app.models.base import BaseModel


class Transfer(BaseModel):
    time = Column(DateTime, nullable=False, index=True)
    currency = Column(String(20), nullable=False, index=True)
    amount = Column(Numeric(38, 18), nullable=False)
    from_account = Column(String(50), nullable=True)
    to_account = Column(String(50), nullable=True)
