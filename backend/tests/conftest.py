import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from applytrack.main import app
from applytrack.db.session import get_db
from applytrack.db.base import Base
from applytrack.core.config import settings
# Import all models
from applytrack.db.models import *

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
settings.database_url = SQLALCHEMY_DATABASE_URL  # Override settings for tasks

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    # Bind the app's session maker to the test engine so tasks use the test DB
    from applytrack.db.session import AsyncSessionLocal
    AsyncSessionLocal.configure(bind=engine)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(db_engine):
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
