from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.games.exceptions import GameNotFound
from backend.models.users_games import Game, UserGame


class Repository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_user_game(self, validated_data: dict) -> Game:
        user_id = validated_data.get("user_id")
        game_name = validated_data.get("name")
        game = await self.get_game_by_filters(name=game_name)
        if not game:
            raise GameNotFound(game_name)

        user_game = UserGame(user_id=user_id, game_id=game.id)
        self._session.add(user_game)
        await self._session.commit()
        await self._session.refresh(user_game)
        return user_game

    async def get_game_by_filters(self, **kwargs) -> Game:
        result = await self._session.execute(select(Game).filter_by(**kwargs))
        game = result.scalars().first()
        return game

    async def get_user_games(self, user_id: int) -> list[UserGame]:
        result = await self._session.execute(
            select(UserGame).options(joinedload(UserGame.game), joinedload(UserGame.user)).filter_by(user_id=user_id)
        )
        return result.scalars().all()

    async def add_games(self, games_data: list[dict]) -> None:
        new_games = []
        for game_data in games_data:
            game = await self.get_game_by_filters(name=game_data.get("name"))
            if not game:
                new_games.append(Game(**game_data))
        if new_games:
            self._session.add_all(new_games)
            await self._session.commit()

    async def get_all_games(self) -> list[Game]:
        result = await self._session.execute(select(Game))
        return result.scalars().all()

    async def delete_user_game(self, validated_data: dict) -> None:
        user_id = validated_data.get("user_id")
        game_name = validated_data.get("name")
        game = await self.get_game_by_filters(name=game_name)
        if not game:
            raise GameNotFound(game_name)
        await self._session.execute(delete(UserGame).filter_by(user_id=user_id, game_id=game.id))
        await self._session.commit()
