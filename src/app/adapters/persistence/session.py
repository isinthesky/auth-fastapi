from __future__ import annotations
from datetime import datetime
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.common.logger import UVICORN_LOGGER
from src.common.exception import DatabaseConnectionError
from src.settings.environment import DataBaseEnviornment


class AsyncRelationDataBaseTemplate:
    _instance = None
    _engine = None
    _session_factory = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            cls._engine = create_async_engine(
                DataBaseEnviornment.get_async_url_connection(),
                echo=True
            )
        return cls._engine

    @classmethod
    def get_session_factory(cls):
        if cls._session_factory is None:
            cls._session_factory = sessionmaker(
                cls.get_engine(),
                class_=AsyncSession,
                expire_on_commit=False
            )
        return cls._session_factory

    @classmethod
    @asynccontextmanager
    async def get_session(cls) -> AsyncGenerator[AsyncSession, None]:
        """비동기 데이터베이스 세션 컨텍스트 매니저"""
        session: AsyncSession = cls.get_session_factory()()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    @classmethod
    def db_session(cls, func):
        """데이터베이스 세션을 자동으로 관리하는 데코레이터"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with cls.get_session() as session:
                return await func(session, *args, **kwargs)
        return wrapper
    
    @classmethod
    def class_db_session(cls, func):
        """클래스 메서드에서 데이터베이스 세션을 자동으로 관리하는 데코레이터"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    
    @classmethod
    async def healthcheck(cls):
        try:
            async with cls.get_session() as session:
                await session.execute(text("SELECT 1"))
                UVICORN_LOGGER.info(f"[{datetime.now()}] : DATABASE CONNECT SUCCESS")
        except Exception as e:
            UVICORN_LOGGER.error(f"Database connection failed: {str(e)}")
            raise DatabaseConnectionError("Failed to connect to database")

    def __init__(self):
        if self._instance is not None:
            raise Exception("Already Initialized AsyncRelationDataBaseTemplate")
        AsyncRelationDataBaseTemplate._instance = self


# Module-level get_session function
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Module-level function to provide a database session."""
    async with AsyncRelationDataBaseTemplate.get_session() as session:
        yield session
