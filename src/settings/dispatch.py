from abc import ABCMeta

from fastapi import FastAPI

from src.app.api.v1.endpoints.users import (
    user_router
)
from src.app.api.v1.endpoints.auth_google import (
    auth_google_router
)


class AbstractDispatcher(metaclass=ABCMeta):

    def __init__(self, app: FastAPI):
        self.app = app

    def execute(self):
        raise NotImplementedError("Must Be Implementation")


class RouterDispatcher(AbstractDispatcher):
    _ALLOWED_ROUTERS = [
        user_router,
        auth_google_router
    ]

    def execute(self):
        [self.app.include_router(routers) for routers in self._ALLOWED_ROUTERS]



class OrmDispatcher(AbstractDispatcher):
    """
        Application과 System의 Seperation of Concern을  위해 Classic Mapping 사용
    """
    def execute(self):
        pass

    

class ExceptionDispatcher(AbstractDispatcher):
    def execute(self):
        from src.common.exception_handler import exception_handler
        from src.common.exception import BaseException
        
        self.app.add_exception_handler(BaseException, exception_handler)


class DispatcherLoader:
    _DISPATCHERS = [RouterDispatcher,OrmDispatcher, ExceptionDispatcher]

    @classmethod
    def execute(cls, app: FastAPI):
        for dispatch in cls._DISPATCHERS:
            dispatch(app).execute()
