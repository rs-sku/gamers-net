from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.core.exceptions import NotFoundException
from backend.games.pg_repository import PgRepository
from backend.games.schemas import (
    CreateUserGameResponseSchema,
    GetGameResponseSchema,
    GetUserGamesResponseSchema,
    UserGameRequestSchema,
)
from backend.models.users_games import Game


class Service:
    def __init__(self, pg_repository: PgRepository) -> None:
        self._pg_repository = pg_repository

    async def add_user_game(
        self, data: UserGameRequestSchema, user_id: int
    ) -> CreateUserGameResponseSchema:
        validated_data = data.model_dump()
        validated_data["user_id"] = user_id
        try:
            user_game = await self._pg_repository.add_user_game(validated_data)
            return CreateUserGameResponseSchema.model_validate(
                user_game, from_attributes=True
            )
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except IntegrityError:
            raise HTTPException(
                status_code=409, detail="Pair user_id and game_id already exists"
            )

    async def get_user_games(self, user_id: int) -> list[GetUserGamesResponseSchema]:
        user_games = await self._pg_repository.get_user_games(user_id)
        return [
            GetUserGamesResponseSchema(
                id=user_game.id,
                user_id=user_game.user.id,
                game_id=user_game.game_id,
                user_nickname=user_game.user.nickname,
                game_name=user_game.game.name,
            )
            for user_game in user_games
        ]

    async def add_games(self, games_data: list[dict]) -> None:
        await self._pg_repository.add_games(games_data)

    async def get_all_games(self) -> list[GetGameResponseSchema]:
        games = await self._pg_repository.get_by_filters(model=Game)
        return [
            GetGameResponseSchema.model_validate(game, from_attributes=True)
            for game in games
        ]

    async def delete_user_game(self, data: UserGameRequestSchema, user_id: int) -> None:
        validated_data = data.model_dump()
        validated_data["user_id"] = user_id
        try:
            await self._pg_repository.delete_user_game(validated_data)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
