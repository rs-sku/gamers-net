from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundException
from backend.models.users_games import User


class PgRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_user(self, validated_data: dict) -> User:
        user = User(**validated_data)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def get_users(self) -> Sequence[User]:
        result = await self._session.execute(select(User))
        users = result.scalars().all()
        return users

    async def get_user_by_filters(self, **kwargs) -> User | None:  # noqa: ANN003
        result = await self._session.execute(select(User).filter_by(**kwargs))
        user = result.scalars().first()
        return user
