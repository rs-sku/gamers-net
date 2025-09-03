from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import CORS_CONFIG
from backend.core.settings import Settings
from backend.core.database import DbSession, close_orm, init_orm
from backend.core.exceptions import http_exception_handler
from backend.core.middlewares import auth_middleware
from backend.data.scripts.load_games import load_games
from backend.games.repository import Repository
from backend.games.routers import games_router
from backend.games.service import Service
from backend.users.routers import users_router

routers = [users_router, games_router]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    print("Startup")
    try:
        await init_orm()
        async with DbSession() as session:
            service = Service(Repository(session))
            await load_games(service)
        print("Loaded games")
        yield
    except Exception as e:
        print(f"Error during startup: {e}")
        raise
    finally:
        print("Shutdown")
        await close_orm()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, **CORS_CONFIG)
app.middleware("http")(auth_middleware)
app.add_exception_handler(HTTPException, http_exception_handler)

for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=Settings.BACKEND_HOST, port=int(Settings.BACKEND_PORT))
