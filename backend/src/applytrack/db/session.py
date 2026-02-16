"""Async SQLAlchemy session factory and FastAPI dependency."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from applytrack.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db():
    """Yield a database session, auto-close on exit."""
    async with AsyncSessionLocal() as session:
        yield session
