import sys
import os
from loguru import logger
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


# 여기서는 예시로 환경 변수를 사용.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_SERIALIZE = os.getenv("LOG_SERIALIZE", "1")  # 1이면 serialize, 0이면 비활성화

# 기존 로거 제거
logger.remove()

# stdout로 로그 출력, JSON 직렬화 옵션(기본값: True/False)
serialize = True if LOG_SERIALIZE == "1" else False

logger.add(
    sys.stdout,
    serialize=serialize,
    level=LOG_LEVEL,
    backtrace=True,
    diagnose=True  # 에러 발생 시 traceback 상세 출력
)
