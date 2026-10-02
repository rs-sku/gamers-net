from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.core.exceptions import NotFoundException
from backend.models.users_games import FriendRequest, User
from backend.users.enums import FriendRequestStatus
from backend.users.neo4j_repository import Neo4jRepository
from backend.users.pg_repository import PgRepository
from backend.users.schemas import (
    GetFriendsResponseSchema,
    UpdatePendingFriendRequestStatusSchema,
    UserLoginSchema,
    UserRequestSchema,
    UserResponseSchema,
)
from backend.users.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


class Service:
    def __init__(self, pg_repository: PgRepository, neo4j_repository: Neo4jRepository) -> None:
        self._pg_repository = pg_repository
        self._neo4j_repository = neo4j_repository

    async def add_user(self, data: UserRequestSchema) -> UserResponseSchema:
        validated_data = data.model_dump()
        validated_data["password"] = get_password_hash(validated_data["password"])
        try:
            user = await self._pg_repository.add(User, validated_data)
            return UserResponseSchema.model_validate(user, from_attributes=True)
        except IntegrityError as e:
            if "users_nickname_key" in str(e.orig):
                raise HTTPException(status_code=409, detail="Nickname already exists")
            elif "users_email_key" in str(e.orig):
                raise HTTPException(status_code=409, detail="Email already exists")
            else:
                raise HTTPException(status_code=409, detail="An unknown integrity error occurred")

    async def get_users(self) -> list[UserResponseSchema]:
        users = await self._pg_repository.get_by_filters(User)
        return [UserResponseSchema.model_validate(user, from_attributes=True) for user in users]

    async def _authenticate_user(
        self, password: str, nickname: str | None = None, email: str | None = None
    ) -> int:
        user = None
        if nickname:
            users = await self._pg_repository.get_by_filters(User, nickname=nickname)
            user = users[0] if users else None
        elif email:
            users = await self._pg_repository.get_by_filters(User, email=email)
            user = users[0] if users else None

        if user is None:
            raise HTTPException(status_code=404, detail="User does not exist")
        if not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Wrong password")
        return user.id

    async def login_user(self, data: UserLoginSchema) -> str:
        user_id = await self._authenticate_user(data.password, data.nickname, data.email)
        return create_access_token(data={"user_id": user_id})

    async def add_friend(self, user_id: int, friend_name: str) -> None:
        users = await self._pg_repository.get_by_filters(User, id=user_id)
        user = users[0] if users else None
        if user is None:
            raise NotFoundException("User not found")

        await self._neo4j_repository.add_friend(user.nickname, friend_name)

    async def get_friends(self, name: str) -> GetFriendsResponseSchema:
        friends = await self._neo4j_repository.get_friends(name)
        return GetFriendsResponseSchema(friends=friends)

    async def get_user_friend_requests_by_status(
        self, user_id: int, status: FriendRequestStatus
    ) -> list[int]:
        requests = await self._pg_repository.get_by_filters(
            FriendRequest,
            requested_user_id=user_id,
            status=status,
        )
        return [request.requesting_user_id for request in requests]

    async def change_pending_friend_request_status(
        self,
        requested_user_id: int,
        requesting_user_id: int,
        new_status: FriendRequestStatus,
    ) -> UpdatePendingFriendRequestStatusSchema:
        requests = await self._pg_repository.get_by_filters(
            model=FriendRequest,
            requested_user_id=requested_user_id,
            requesting_user_id=requesting_user_id,
        )
        request = requests[0] if requests else None
        if request is None:
            raise NotFoundException("Friend request not found")

        if request.status != FriendRequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Friend request status must be 'PENDING'")

        request.status = new_status
        updated = await self._pg_repository.update(request)
        return UpdatePendingFriendRequestStatusSchema(new_status=updated.status)
