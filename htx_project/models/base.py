"""
Base model for HTX Project
Contains common fields and methods for all models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Text
from sqlalchemy.orm import declared_attr
from db.session import Base
import uuid


class BaseModel(Base):
    """Base model with common fields"""
    
    __abstract__ = True
    
    # Common fields
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Optional fields for tracking
    source = Column(String(50), nullable=True, comment="Data source (htx, 3commas, file, etc.)")
    external_id = Column(String(100), nullable=True, comment="External ID from source system")
    notes = Column(Text, nullable=True, comment="Additional notes")
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name"""
        return cls.__name__.lower()
    
    def __repr__(self):
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def generate_external_id(cls):
        """Generate a unique external ID"""
        return str(uuid.uuid4())
