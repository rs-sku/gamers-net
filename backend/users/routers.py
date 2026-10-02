from fastapi import APIRouter, Request, Response

from backend.users.dependencies import ServiceDep
from backend.users.enums import FriendRequestStatus
from backend.users.schemas import (
    FriendRequestResponseSchema,
    GetFriendsResponseSchema,
    UpdatePendingFriendRequestStatusSchema,
    UserLoginSchema,
    UserRequestSchema,
    UserResponseSchema,
)

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.post("", response_model=UserResponseSchema, status_code=201)
async def create_user(
    data: UserRequestSchema, service: ServiceDep
) -> UserResponseSchema:
    response = await service.add_user(data)
    return response


@users_router.post("/login", response_model=bool, status_code=201)
async def login(response: Response, data: UserLoginSchema, service: ServiceDep) -> bool:
    token = await service.login_user(data)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return True


@users_router.get("", response_model=list[UserResponseSchema], status_code=200)
async def get_users(service: ServiceDep) -> list[UserResponseSchema]:
    response = await service.get_users()
    return response


@users_router.post("/logout", response_model=bool, status_code=201)
async def logout(response: Response) -> bool:
    response.delete_cookie(key="access_token")
    return True


@users_router.get("/me", response_model=UserResponseSchema, status_code=200)
async def get_current_user(request: Request, service: ServiceDep) -> UserResponseSchema:
    return await service.get_current_user(request.state.user_id)


@users_router.post(
    "/friend-request", response_model=FriendRequestResponseSchema, status_code=201
)
async def add_friend_request(
    service: ServiceDep, friend_name: str, request: Request
) -> FriendRequestResponseSchema:
    user_id = request.state.user_id
    return await service.add_pending_friend_request(user_id, friend_name)


@users_router.get("/friends", response_model=GetFriendsResponseSchema, status_code=200)
async def get_friends(service: ServiceDep, name: str) -> GetFriendsResponseSchema:
    friends = await service.get_friends(name)
    return friends


@users_router.get(
    "/incoming-friend-requests",
    response_model=list[FriendRequestResponseSchema],
    status_code=200,
)
async def get_incoming_friend_requests(
    request: Request,
    status: FriendRequestStatus,
    service: ServiceDep,
) -> list[FriendRequestResponseSchema]:
    user_id = request.state.user_id
    return await service.get_user_incoming_friend_requests_by_status(user_id, status)


@users_router.get(
    "/outgoing-friend-requests",
    response_model=list[FriendRequestResponseSchema],
    status_code=200,
)
async def get_outgoing_friend_requests(
    request: Request,
    status: FriendRequestStatus,
    service: ServiceDep,
) -> list[FriendRequestResponseSchema]:
    user_id = request.state.user_id
    return await service.get_user_outgoing_friend_requests_by_status(user_id, status)


@users_router.patch(
    "/pending-friend-requests",
    response_model=UpdatePendingFriendRequestStatusSchema,
    status_code=200,
)
async def process_pending_friend_request(
    request: Request,
    requesting_user_id: int,
    data: UpdatePendingFriendRequestStatusSchema,
    service: ServiceDep,
) -> UpdatePendingFriendRequestStatusSchema:
    requested_user_id = request.state.user_id
    return await service.process_pending_friend_request(
        requested_user_id=requested_user_id,
        requesting_user_id=requesting_user_id,
        new_status=data.new_status,
    )
