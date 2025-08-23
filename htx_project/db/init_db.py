"""
Database initialization for HTX Project
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import init_db as create_tables
from core.config import settings

logger = logging.getLogger(__name__)


async def init_db():
    """Initialize database with tables and initial data"""
    try:
        # Create tables
        await create_tables()
        logger.info("Database initialized successfully")
        
        # Add any initial data here if needed
        # await create_initial_data()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def create_initial_data():
    """Create initial data for the application"""
    # This function can be used to add initial data
    # For example, default currencies, exchange configurations, etc.
    pass


async def reset_db():
    """Reset database (drop and recreate all tables)"""
    from db.session import engine, Base
    
    try:
        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("All tables dropped")
            
            # Recreate tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("All tables recreated")
            
            # Initialize with initial data
            await create_initial_data()
            
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        raise
