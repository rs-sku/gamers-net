from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.base_pg_repository import BasePgRepository
from backend.models.users_games import FriendRequest


class PgRepository(BasePgRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_friend_request_for_update(
        self, requesting_user_id: int, requested_user_id: int
    ) -> FriendRequest | None:
        result = await self._session.execute(
            select(FriendRequest)
            .filter_by(
                requesting_user_id=requesting_user_id,
                requested_user_id=requested_user_id,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def add_friend_request(self, validated_data: dict) -> FriendRequest:
        request = FriendRequest(**validated_data)
        self._session.add(request)
        await self._session.commit()
        await self._session.refresh(request)
        return request
