from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_session
from backend.users.repository import Repository
from backend.users.service import Service


def get_repository(session: AsyncSession = Depends(get_session)) -> Repository:
    return Repository(session)


def get_service(repo: Repository = Depends(get_repository)) -> Service:
    return Service(repo)


ServiceDep = Annotated[Service, Depends(get_service)]
