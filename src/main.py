import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings.config import lifespan, logger
from .settings.dispatch import DispatcherLoader
from icecream import ic

class AuthApplication:

    app = FastAPI(
        title="Auth API",
        description="Auth API",
        lifespan=lifespan,
        docs_url="/docs"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://facreport.iptime.org:8007", "http://localhost:8007", "http://facreport.iptime.org:8000", "http://facreport.iptime.org:8001", "http://facreport.iptime.org:8002", "http://localhost:8001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    @app.get("/api/v1/auth")
    async def auth_check():
        return {"message": "Auth API is running"}

    def __call__(self, *args, **kwargs):
        logger.info("AuthApplication called")
        
        DispatcherLoader.execute(self.app)
        return self.app

app = AuthApplication()

def start():
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
