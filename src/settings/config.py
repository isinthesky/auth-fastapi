from contextlib import asynccontextmanager

from fastapi import FastAPI

from .dispatch import DispatcherLoader
from src.app.adapters.persistence.session import AsyncRelationDataBaseTemplate
from src.common.logger import UVICORN_LOGGER
from src.common.exception import DatabaseConnectionError
# from .redis import UserRedisTemplate

@asynccontextmanager
async def lifespan(app: FastAPI):
    database = AsyncRelationDataBaseTemplate()
    try:
        await database.healthcheck()
    except DatabaseConnectionError as e:
        UVICORN_LOGGER.error(f"Startup failed: {e}")
        raise e

    DispatcherLoader.execute(app)

    yield
