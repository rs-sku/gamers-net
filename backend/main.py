from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from neo4j import AsyncDriver, AsyncGraphDatabase

from backend.core.config import CORS_CONFIG
from backend.core.database_pg import DbSession, close_orm, init_orm
from backend.core.exceptions import http_exception_handler
from backend.core.middlewares import auth_middleware
from backend.core.settings import Settings
from backend.data.scripts.load_games import load_games
from backend.games.pg_repository import PgRepository
from backend.games.routers import games_router
from backend.games.service import Service
from backend.users.routers import users_router

routers = [users_router, games_router]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    print("Startup")
    neo4j_driver: AsyncDriver = AsyncGraphDatabase.driver(
        Settings.NEO4J_URI,
        auth=(Settings.NEO4J_LOGIN, Settings.NEO4J_PASSWORD),
    )
    try:
        await init_orm()
        await neo4j_driver.verify_connectivity()

        async with DbSession() as session:
            service = Service(PgRepository(session))
            await load_games(service)
        print("Loaded games")

        app.state.neo4j_driver = neo4j_driver

        yield
    except Exception as e:
        print(f"Error during startup: {e}")
        raise
    finally:
        print("Shutdown")
        await close_orm()
        await neo4j_driver.close()


app = FastAPI(lifespan=lifespan)
app.middleware("http")(auth_middleware)
app.add_middleware(CORSMiddleware, **CORS_CONFIG)
app.add_exception_handler(HTTPException, http_exception_handler)

for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=Settings.BACKEND_HOST, port=int(Settings.BACKEND_PORT))
