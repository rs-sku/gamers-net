from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_session
from backend.games.pg_repository import PgRepository
from backend.games.service import Service


def get_repository(session: AsyncSession = Depends(get_session)) -> PgRepository:
    return PgRepository(session)


def get_service(repo: PgRepository = Depends(get_repository)) -> Service:
    return Service(repo)


ServiceDep = Annotated[Service, Depends(get_service)]
