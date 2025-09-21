from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.games.exceptions import GameNotFound
from backend.games.repository import Repository
from backend.games.schemas import (
    CreateUserGameResponseSchema,
    GetGameResponseSchema,
    GetUserGamesResponseSchema,
    UserGameRequestSchema,
)


class Service:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def add_user_game(
        self, data: UserGameRequestSchema, user_id: int
    ) -> CreateUserGameResponseSchema:
        validated_data = data.model_dump()
        validated_data["user_id"] = user_id
        try:
            user_game = await self.repository.add_user_game(validated_data)
            return CreateUserGameResponseSchema.model_validate(
                user_game, from_attributes=True
            )
        except GameNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except IntegrityError:
            raise HTTPException(
                status_code=409, detail="Pair user_id and game_id already exists"
            )

    async def get_user_games(self, user_id: int) -> list[GetUserGamesResponseSchema]:
        user_games = await self.repository.get_user_games(user_id)
        for user_game in user_games:
            user_game.user_nickname = user_game.user.nickname
            user_game.game_name = user_game.game.name
        return [
            GetUserGamesResponseSchema.model_validate(user_game, from_attributes=True)
            for user_game in user_games
        ]

    async def add_games(self, games_data: list[dict]) -> None:
        await self.repository.add_games(games_data)

    async def get_all_games(self) -> list[GetGameResponseSchema]:
        games = await self.repository.get_all_games()
        return [
            GetGameResponseSchema.model_validate(game, from_attributes=True)
            for game in games
        ]

    async def delete_user_game(self, data: UserGameRequestSchema, user_id: int) -> None:
        validated_data = data.model_dump()
        validated_data["user_id"] = user_id
        try:
            await self.repository.delete_user_game(validated_data)
        except GameNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
