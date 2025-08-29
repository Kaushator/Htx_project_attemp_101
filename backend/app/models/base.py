"""
Base ORM model with common fields
"""

from datetime import datetime, UTC
from sqlalchemy import Column, Integer, DateTime, String, Text
from sqlalchemy.orm import declared_attr
from app.db.session import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    source = Column(String(50), nullable=True)
    external_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
