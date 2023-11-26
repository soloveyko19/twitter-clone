import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio.engine import create_async_engine
from typing import AsyncGenerator
import asyncio

from app import init_app
from database.models import Base, async_session, User
from conf import (
    TEST_POSTGRES_USER,
    TEST_POSTGRES_PASSWORD,
    TEST_POSTGRES_HOST,
    TEST_POSTGRES_DB,
)

db_url_test = f"postgresql+asyncpg://{TEST_POSTGRES_USER}:{TEST_POSTGRES_PASSWORD}@{TEST_POSTGRES_HOST}/{TEST_POSTGRES_DB}"
engine_test = create_async_engine(
    url=db_url_test,
)

async_session.configure(bind=engine_test)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    app = init_app()
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture(autouse=True, scope="session")
async def init_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def user_test() -> AsyncGenerator["User", None]:
    async with async_session() as session:
        users = [
            User(id=i, name=f"test_{i}", api_key=f"test_{i}")
            for i in range(1, 4)
        ]
        session.add_all(users)
        await session.commit()
    yield users[1]
    async with async_session() as session:
        for user in users:
            await session.delete(user)
        await session.commit()


@pytest.fixture
async def as_session():
    return async_session
