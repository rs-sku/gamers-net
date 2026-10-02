from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.core.exceptions import NotFoundException
from backend.models.users_games import FriendRequest, User
from backend.users.enums import FriendRequestStatus
from backend.users.neo4j_repository import Neo4jRepository
from backend.users.pg_repository import PgRepository
from backend.users.schemas import (
    FriendRequestResponseSchema,
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

    async def get_current_user(self, user_id: int) -> UserResponseSchema:
        users = await self._pg_repository.get_by_filters(User, id=user_id)
        if not users:
            raise NotFoundException("User not found")
        return UserResponseSchema.model_validate(users[0], from_attributes=True)

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

    async def get_friends(self, name: str) -> GetFriendsResponseSchema:
        friends = await self._neo4j_repository.get_friends(name)
        return GetFriendsResponseSchema(friends=friends)

    async def get_user_incoming_friend_requests_by_status(
        self, user_id: int, status: FriendRequestStatus
    ) -> list[FriendRequestResponseSchema]:
        requests = await self._pg_repository.get_by_filters(
            FriendRequest,
            requested_user_id=user_id,
            status=status,
        )
        return [
            FriendRequestResponseSchema.model_validate(request, from_attributes=True)
            for request in requests
        ]

    async def get_user_outgoing_friend_requests_by_status(
        self, user_id: int, status: FriendRequestStatus
    ) -> list[FriendRequestResponseSchema]:
        requests = await self._pg_repository.get_by_filters(
            FriendRequest,
            requesting_user_id=user_id,
            status=status,
        )
        return [
            FriendRequestResponseSchema.model_validate(request, from_attributes=True)
            for request in requests
        ]

    async def add_pending_friend_request(
        self, user_id: int, friend_name: str
    ) -> FriendRequestResponseSchema:
        user = await self.get_current_user(user_id)
        users = await self._pg_repository.get_by_filters(User, nickname=friend_name)
        friend = users[0] if users else None
        if friend is None:
            raise NotFoundException("User not found")
        if friend.id == user_id:
            raise HTTPException(status_code=400, detail="Cannot send a friend request to yourself")

        if friend_name in await self._neo4j_repository.get_friends(user.nickname):
            raise HTTPException(status_code=400, detail="Users are already friends")

        incoming_requests = await self._pg_repository.get_by_filters(
            FriendRequest,
            requesting_user_id=friend.id,
            requested_user_id=user_id,
        )
        if any(request.status != FriendRequestStatus.REJECTED for request in incoming_requests):
            raise HTTPException(
                status_code=400, detail="Valid incoming friend request already exists"
            )

        request = await self._pg_repository.get_friend_request_for_update(
            requesting_user_id=user_id,
            requested_user_id=friend.id,
        )

        if request is not None and request.status != FriendRequestStatus.REJECTED:
            raise HTTPException(
                status_code=400, detail="Valid outgoing friend request already exists"
            )

        try:
            if request is not None:
                request.status = FriendRequestStatus.PENDING
                request = await self._pg_repository.update(request)
            else:
                request = await self._pg_repository.add_friend_request(
                    {
                        "requesting_user_id": user_id,
                        "requested_user_id": friend.id,
                        "status": FriendRequestStatus.PENDING,
                    }
                )
        except IntegrityError:
            await self._pg_repository.rollback()
            raise HTTPException(status_code=409, detail="Friend request already exists")
        return FriendRequestResponseSchema.model_validate(request, from_attributes=True)

    async def process_pending_friend_request(
        self,
        requested_user_id: int,
        requesting_user_id: int,
        new_status: FriendRequestStatus,
    ) -> UpdatePendingFriendRequestStatusSchema:
        if new_status not in (
            FriendRequestStatus.ACCEPTED,
            FriendRequestStatus.REJECTED,
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Friend request new status can only be {FriendRequestStatus.ACCEPTED} or "
                f"{FriendRequestStatus.REJECTED}",
            )

        request = await self._pg_repository.get_friend_request_for_update(
            requesting_user_id=requesting_user_id,
            requested_user_id=requested_user_id,
        )
        if request is None:
            raise NotFoundException("Friend request not found")

        if request.status != FriendRequestStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Current friend request status must be '{FriendRequestStatus.PENDING}'",
            )

        # TODO: Change for transactional outbox
        friendship = None
        try:
            if new_status == FriendRequestStatus.ACCEPTED:
                sender = await self.get_current_user(requesting_user_id)
                receiver = await self.get_current_user(requested_user_id)
                friendship = (sender.nickname, receiver.nickname)
                await self._neo4j_repository.add_friend(*friendship)

            request.status = new_status
            await self._pg_repository.update(request, refresh=False)
        except Exception:
            try:
                if friendship is not None:
                    await self._neo4j_repository.remove_friend(*friendship)
            finally:
                await self._pg_repository.rollback()
            raise
        return UpdatePendingFriendRequestStatusSchema(new_status=new_status)
