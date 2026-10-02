from fastapi import APIRouter, Request, Response

from backend.users.dependencies import ServiceDep
from backend.users.schemas import (
    GetFriendsResponseSchema,
    UserLoginSchema,
    UserRequestSchema,
    UserResponseSchema,
)

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.post("", response_model=UserResponseSchema, status_code=201)
async def create_user(data: UserRequestSchema, service: ServiceDep) -> UserResponseSchema:
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


@users_router.post("/friend", response_model=bool, status_code=201)
async def add_friend(service: ServiceDep, friend_name: str, request: Request) -> bool:
    user_id = request.state.user_id
    await service.add_friend(user_id, friend_name)
    return True


@users_router.get("/friends", response_model=GetFriendsResponseSchema, status_code=200)
async def get_friends(service: ServiceDep, name: str) -> GetFriendsResponseSchema:
    friends = await service.get_friends(name)
    return friends
