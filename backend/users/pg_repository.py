from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.base_pg_repository import BasePgRepository
from backend.models.users_games import FriendRequest


class PgRepository(BasePgRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def add_friend_request(self, validated_data: dict) -> FriendRequest:
        request = FriendRequest(**validated_data)
        self._session.add(request)
        await self._session.commit()
        await self._session.refresh(request)
        return request
