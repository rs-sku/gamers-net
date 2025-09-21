from fastapi import APIRouter, Response

from backend.users.dependencies import ServiceDep
from backend.users.schemas import UserLoginSchema, UserRequestSchema, UserResponseSchema

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
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="Lax")
    return True


@users_router.get("", response_model=list[UserResponseSchema], status_code=200)
async def get_users(service: ServiceDep) -> list[UserResponseSchema]:
    response = await service.get_users()
    return response


@users_router.post("/logout", response_model=bool, status_code=201)
async def logout(response: Response) -> bool:
    response.delete_cookie(key="access_token")
    return True
