from typing import Sequence

from sqlalchemy import RowMapping, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.base_pg_repository import BasePgRepository
from backend.core.exceptions import NotFoundException
from backend.core.pagination import Pagination
from backend.models.users_games import Game, User, UserGame


class PgRepository(BasePgRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def add_user_game(self, validated_data: dict) -> UserGame:
        user_id = validated_data["user_id"]
        game_name = validated_data["name"]
        games = await self.get_by_filters(model=Game, name=game_name)
        game = games[0] if games else None

        if game is None:
            raise NotFoundException(f"{game_name} not found")

        user_game = UserGame(user_id=user_id, game_id=game.id)
        self._session.add(user_game)
        await self._session.commit()
        await self._session.refresh(user_game)
        return user_game

    async def get_user_games(self, user_id: int, pagination: Pagination) -> Sequence[RowMapping]:
        result = await self._session.execute(
            select(
                UserGame.id,
                UserGame.user_id,
                UserGame.game_id,
                User.nickname.label("user_nickname"),
                Game.name.label("game_name"),
            )
            .join(User, User.id == UserGame.user_id)
            .join(Game, Game.id == UserGame.game_id)
            .where(UserGame.user_id == user_id)
            .order_by(UserGame.id)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        return result.mappings().all()

    async def add_games(self, games_data: list[dict]) -> None:
        new_games = []
        for game_data in games_data:
            games = await self.get_by_filters(model=Game, name=game_data["name"])
            game = games[0] if games else None
            if game is None:
                new_games.append(Game(**game_data))
        if new_games:
            self._session.add_all(new_games)
            await self._session.commit()

    async def delete_user_game(self, validated_data: dict) -> None:
        user_id = validated_data["user_id"]
        game_name = validated_data["name"]
        games = await self.get_by_filters(model=Game, name=game_name)
        game = games[0] if games else None

        if game is None:
            raise NotFoundException(f"{game_name} not found")
        await self._session.execute(delete(UserGame).filter_by(user_id=user_id, game_id=game.id))
        await self._session.commit()
