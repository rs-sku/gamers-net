from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy import RowMapping, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.pagination import Pagination
from backend.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BasePgRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def rollback(self) -> None:
        await self._session.rollback()

    async def add(
        self,
        model: type[ModelT],
        validated_data: dict,
    ) -> ModelT:
        obj = model(**validated_data)
        self._session.add(obj)
        await self._session.commit()
        await self._session.refresh(obj)
        return obj

    async def get_by_filters(
        self,
        model: type[ModelT],
        **filters: object,
    ) -> Sequence[ModelT]:
        query = await self._session.execute(select(model).filter_by(**filters))
        result = query.scalars().all()
        return result

    async def get_page(
        self,
        model: type[ModelT],
        columns: tuple[str, ...],
        pagination: Pagination,
        **filters: object,
    ) -> Sequence[RowMapping]:
        statement = (
            select(*(getattr(model, column) for column in columns))
            .filter_by(**filters)
            .order_by(getattr(model, "id"))
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        result = await self._session.execute(statement)
        return result.mappings().all()

    async def update(self, model: ModelT, refresh: bool = True) -> ModelT:
        self._session.add(model)
        await self._session.commit()
        if refresh:
            await self._session.refresh(model)
        return model
