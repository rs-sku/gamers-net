from typing import Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundException
from backend.models.base import Base
from backend.models.users_games import FriendRequest, User


ModelT = TypeVar("ModelT", bound=Base)


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
        query = await self._session.execute(select(User))
        result = query.scalars().all()
        return result

    async def get_by_filters(self, model: type[ModelT], **kwargs) -> Sequence[ModelT]:  # noqa: ANN003
        query = await self._session.execute(select(model).filter_by(**kwargs))
        result = query.scalars().all()
        return result

    async def add_friend_request(self, validated_data: dict) -> FriendRequest:
        request = FriendRequest(**validated_data)
        self._session.add(request)
        await self._session.commit()
        await self._session.refresh(request)
        return request
