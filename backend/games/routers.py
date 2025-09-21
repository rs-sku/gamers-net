from fastapi import APIRouter, Request

from backend.games.dependencies import ServiceDep
from backend.games.schemas import (
    CreateUserGameResponseSchema,
    GetGameResponseSchema,
    GetUserGamesResponseSchema,
    UserGameRequestSchema,
)

games_router = APIRouter(prefix="/api/v1/games", tags=["games"])


@games_router.post("", response_model=CreateUserGameResponseSchema, status_code=201)
async def create_user_game(
    request: Request, data: UserGameRequestSchema, service: ServiceDep
) -> CreateUserGameResponseSchema:
    user_id = request.state.user_id
    response = await service.add_user_game(data, user_id)
    return response


@games_router.get("", response_model=list[GetUserGamesResponseSchema])
async def get_user_games(
    request: Request, service: ServiceDep
) -> list[GetUserGamesResponseSchema]:
    user_id = request.state.user_id
    response = await service.get_user_games(user_id)
    return response


@games_router.get("/all", response_model=list[GetGameResponseSchema])
async def get_all_games(service: ServiceDep) -> list[GetGameResponseSchema]:
    response = await service.get_all_games()
    return response


@games_router.delete("", status_code=204)
async def delete_user_game(
    request: Request, data: UserGameRequestSchema, service: ServiceDep
) -> None:
    user_id = request.state.user_id
    await service.delete_user_game(data, user_id)
