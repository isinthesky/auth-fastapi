from fastapi import Depends
from src.app.adapters.persistence.repositories.user_repository import UserRepository
from src.app.adapters.persistence.session import get_session
from src.app.core.services.auth_service import AuthService

async def get_user_repository(
    session = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)

async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(user_repository) 