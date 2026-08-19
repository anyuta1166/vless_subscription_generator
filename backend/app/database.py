from collections.abc import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


database_url = URL.create(
    drivername="mysql+asyncmy",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)


engine = create_async_engine(
    database_url,
    pool_pre_ping=True,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
