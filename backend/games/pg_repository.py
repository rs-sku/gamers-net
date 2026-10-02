from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.core.exceptions import NotFoundException
from backend.models.users_games import Game, UserGame


class PgRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_user_game(self, validated_data: dict) -> UserGame:
        user_id = validated_data["user_id"]
        game_name = validated_data["name"]
        game = await self.get_game_by_filters(name=game_name)
        if not game:
            raise NotFoundException(f"{game_name} not found")

        user_game = UserGame(user_id=user_id, game_id=game.id)
        self._session.add(user_game)
        await self._session.commit()
        await self._session.refresh(user_game)
        return user_game

    async def get_game_by_filters(self, **kwargs) -> Game | None:  # noqa: ANN003
        result = await self._session.execute(select(Game).filter_by(**kwargs))
        game = result.scalars().first()
        return game

    async def get_user_games(self, user_id: int) -> Sequence[UserGame]:
        result = await self._session.execute(
            select(UserGame)
            .options(joinedload(UserGame.game), joinedload(UserGame.user))
            .filter_by(user_id=user_id)
        )
        return result.scalars().all()

    async def add_games(self, games_data: list[dict]) -> None:
        new_games = []
        for game_data in games_data:
            game = await self.get_game_by_filters(name=game_data["name"])
            if not game:
                new_games.append(Game(**game_data))
        if new_games:
            self._session.add_all(new_games)
            await self._session.commit()

    async def get_all_games(self) -> Sequence[Game]:
        result = await self._session.execute(select(Game))
        return result.scalars().all()

    async def delete_user_game(self, validated_data: dict) -> None:
        user_id = validated_data["user_id"]
        game_name = validated_data["name"]
        game = await self.get_game_by_filters(name=game_name)
        if not game:
            raise NotFoundException(f"{game_name} not found")
        await self._session.execute(delete(UserGame).filter_by(user_id=user_id, game_id=game.id))
        await self._session.commit()
