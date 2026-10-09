from typing import cast

from sqlalchemy import Table, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.core.settings import Settings
from backend.models.base import Base
from backend.models.users_games import FriendRequest

# TODO measure pool characteristics
engine = create_async_engine(
    f"postgresql+asyncpg://{Settings.POSTGRES_USER}:{Settings.POSTGRES_PASSWORD}@{Settings.POSTGRES_HOST}:"
    f"{Settings.POSTGRES_PORT}/{Settings.POSTGRES_DB}"
)
DbSession = async_sessionmaker(engine, expire_on_commit=False)


async def init_orm() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_friend_request_users "
                "ON friend_requests (requesting_user_id, requested_user_id)"
            )
        )
        for index in cast(Table, FriendRequest.__table__).indexes:
            await conn.run_sync(lambda conn: index.create(conn, checkfirst=True))


async def close_orm() -> None:
    await engine.dispose()
