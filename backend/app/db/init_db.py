"""
Database init/reset helpers
"""

from app.db.session import engine, Base


async def init_db():
    async with engine.begin() as conn:
        # Import models to register metadata
        from app.models import trade, deposit, withdraw, transfer  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
