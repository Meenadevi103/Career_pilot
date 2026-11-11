"""Pytest configuration and fixtures using real PostgreSQL test database."""

import asyncio
import sys
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure selector event loop on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.config import settings
from app.db.base import Base
from app.db.init_test_db import init_test_db
from app.db.session import get_db
from app.main import app

# Ensure test database exists
init_test_db()

# Synchronously initialize tables in test database once at test suite startup
_sync_url = settings.TEST_DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
_sync_engine = create_engine(_sync_url)
Base.metadata.drop_all(_sync_engine)
Base.metadata.create_all(_sync_engine)
_sync_engine.dispose()

# Asynchronous test engine
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=False,
    future=True,
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(autouse=True)
async def clean_database():
    """Clean up table records between tests to guarantee isolated test runs."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional test database session."""
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client overriding get_db to connect strictly to test database."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestAsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()
