from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_session
from backend.users.neo4j_repository import Neo4jRepository
from backend.users.pg_repository import PgRepository
from backend.users.service import Service


def get_pg_repository(session: AsyncSession = Depends(get_session)) -> PgRepository:
    return PgRepository(session)


def get_neo_4j_repository(request: Request) -> Neo4jRepository:
    return Neo4jRepository(request.app.state.neo4j_driver)


def get_service(
    pg_repo: PgRepository = Depends(get_pg_repository),
    neo4j_repo: Neo4jRepository = Depends(get_neo_4j_repository),
) -> Service:
    return Service(pg_repo, neo4j_repo)


ServiceDep = Annotated[Service, Depends(get_service)]
