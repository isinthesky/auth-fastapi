from abc import ABCMeta

from fastapi import FastAPI

from src.app.api.v1.endpoints.auth import (
    user_router
)


class AbstractDispatcher(metaclass=ABCMeta):

    def __init__(self, app: FastAPI):
        self.app = app

    def execute(self):
        raise NotImplementedError("Must Be Implementation")


class RouterDispatcher(AbstractDispatcher):
    _ALLOWED_ROUTERS = [
        user_router
    ]

    def execute(self):
        [self.app.include_router(routers) for routers in self._ALLOWED_ROUTERS]


class OrmDispatcher(AbstractDispatcher):
    """
        Application과 System의 Seperation of Concern을  위해 Classic Mapping 사용
    """
    def execute(self):
        from sqlalchemy.orm import registry

        from src.app.core.domain.entities.user import UserEntity
        from src.app.core.domain.entities.token import TokenEntity
        from src.settings.orm import User, TokenModel
        from sqlalchemy.orm import relationship
        
        # Entity 와 DataBase Table Mapping
        mapper_register = registry()

        # User Resource Mapper
        mapper_register.map_imperatively(
            UserEntity,
            User.__table__,
            properties={
                'tasks': relationship("TaskEntity", back_populates="user")
            }
        )

        # Token Resource Mapper
        mapper_register.map_imperatively(
            TokenEntity,
            TokenModel.__table__,
            properties={
                'user': relationship("UserEntity", back_populates="tokens")
            }
        )

        return mapper_register



class DispatcherLoader:
    _DISPATCHERS = [RouterDispatcher, OrmDispatcher]

    @classmethod
    def execute(cls, app: FastAPI):
        for dispatch in cls._DISPATCHERS:
            dispatch(app).execute()
