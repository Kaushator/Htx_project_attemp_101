"""
Модуль для переноса базы данных проекта HTX на PostgreSQL
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection
from app.models.base import Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("postgres_migration")

# Constants
PG_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://htx:htx@localhost:5432/htx")


async def check_postgres_connection() -> bool:
    """Check if PostgreSQL connection works"""
    engine = None
    try:
        engine = create_async_engine(PG_URL, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            await conn.commit()
            value = result.scalar_one()
            return value == 1
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {e}")
        return False
    finally:
        if engine:
            await engine.dispose()


async def create_tables() -> bool:
    """Create all tables in PostgreSQL"""
    engine = None
    try:
        engine = create_async_engine(PG_URL, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False
    finally:
        if engine:
            await engine.dispose()


async def list_tables() -> List[str]:
    """List all tables in PostgreSQL database"""
    engine = None
    try:
        engine = create_async_engine(PG_URL, echo=False)
        tables = []
        
        # Get inspector
        insp = inspect(engine)
        async with engine.connect() as conn:
            tables = await conn.run_sync(lambda sync_conn: insp.get_table_names(connection=sync_conn))
        
        return tables
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return []
    finally:
        if engine:
            await engine.dispose()


async def main():
    """Main function to check PostgreSQL setup"""
    logger.info("Checking PostgreSQL connection...")
    
    if not await check_postgres_connection():
        logger.error("Failed to connect to PostgreSQL")
        return False
    
    logger.info("PostgreSQL connection successful")
    
    logger.info("Creating database tables...")
    if not await create_tables():
        logger.error("Failed to create tables")
        return False
    
    tables = await list_tables()
    logger.info(f"Created {len(tables)} tables: {', '.join(tables)}")
    
    logger.info("PostgreSQL setup completed successfully")
    return True


if __name__ == "__main__":
    if asyncio.run(main()):
        print("\n✅ PostgreSQL setup successful")
        sys.exit(0)
    else:
        print("\n❌ PostgreSQL setup failed")
        sys.exit(1)
