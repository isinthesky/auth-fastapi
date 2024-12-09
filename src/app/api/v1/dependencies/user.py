from fastapi import Depends
from src.app.core.services.user_service import UserService
from src.app.adapters.persistence.repositories.user_repository import UserRepository
from src.app.adapters.persistence.session import get_session

async def get_user_service(
    session = Depends(get_session)
) -> UserService:
    user_repository = UserRepository(session)
    return UserService(user_repository)