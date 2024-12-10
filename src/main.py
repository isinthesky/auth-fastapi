import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings.config import lifespan, logger
from .settings.environment import config
from .common.exception import BaseException, AuthenticationException
from icecream import ic

app = FastAPI(
    title="Auth API",
    description="Authentication and Authorization API using FastAPI",
    version="1.0.0"
)

class AuthApplication:

    app = FastAPI(
        title="Auth API",
        description="Auth API",
        lifespan=lifespan,
        docs_url="/docs"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=(
            config["SSO_ALLOW_ORIGIN"]
            if config["PROJECT_STATE"] == "PRODUCT"
            else config["SSO_ALLOW_ORIGIN_DEV"]
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AuthenticationException)
    async def custom_response_handler(request, err):
        logger.error(f"AuthenticationException occurred: {err}")
        ic("AuthenticationException", err)
        return err.to_response()

    @app.exception_handler(BaseException)
    async def http_exception_handler(request, err):
        logger.error(f"BaseException occurred: {err}")
        ic("BaseException", err)
        return err.to_response()


    def __call__(self, *args, **kwargs):
        logger.info("AuthApplication called")
        return self.app

app = AuthApplication()

def start():
    uvicorn.run("src.main:app", host="0.0.0.0", port=8008, reload=True)

if __name__ == "__main__":
    start()
