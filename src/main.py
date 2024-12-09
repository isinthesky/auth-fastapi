import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings.config import lifespan
from .settings.environment import config
from .common.exception import BaseException, AuthenticationException
from icecream import ic
from src.app.infrastructure.monitoring.prometheus import setup_monitoring

app = FastAPI(
    title="Auth API",
    description="Authentication and Authorization API using FastAPI",
    version="1.0.0"
)

setup_monitoring(app)

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
        ic("AuthenticationException", err)
        return err.to_response()

    @app.exception_handler(BaseException)
    async def http_exception_handler(request, err):
        ic("BaseException", err)
        return err.to_response()


    def __call__(self, *args, **kwargs):
        return self.app

app = AuthApplication()



def start():
    # application 객체 대신 문자열로 모듈 경로 전달
    uvicorn.run("src.main:app", host="0.0.0.0", port=8081, reload=True)

# If you want to run the start function when the script is executed directly
if __name__ == "__main__":
    start()
