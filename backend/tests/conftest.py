"""Shared fixtures for backend tests.

Uses an in-memory SQLite database for speed and full isolation.
Every test gets fresh tables via the autouse setup_db fixture.
"""

# Override settings BEFORE any app import.
from applytrack.core.config import settings  # noqa: E402

settings.database_url = "sqlite+aiosqlite://"
settings.celery_always_eager = True

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from applytrack.db.base import Base  # noqa: E402
from applytrack.db.session import get_db  # noqa: E402
from applytrack.main import app  # noqa: E402
from applytrack.workers.celery_app import celery_app as _celery  # noqa: E402

# Force eager Celery with in-memory broker (no Redis needed).
_celery.conf.update(
    task_always_eager=True,
    task_eager_propagates=False,
    task_store_eager_result=True,
    broker_url="memory://",
    result_backend="cache+memory://",
)

_engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False})
_TestSession = async_sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    import applytrack.db.models  # noqa: F401

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_db):
    async with _TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ── Auth helpers ──


async def register_and_login(
    client: AsyncClient,
    email: str = "user@test.com",
    password: str = "Str0ng!Pass",
) -> tuple[str, dict]:
    """Register + login → (token, headers)."""
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    token = resp.json()["access_token"]
    return token, {"Authorization": f"Bearer {token}"}
