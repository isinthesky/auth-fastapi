from datetime import datetime
from typing import Optional
from fastapi import HTTPException

from src.app.core.domain.entities.user import UserEntity
from src.app.core.domain.entities.token import TokenEntity
from src.app.core.domain.value_objects import Email
from src.app.core.ports.user_port import UserRepositoryPort
from src.app.core.ports.token_port import TokenRepositoryPort

class AuthService:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    async def login(self, email: str, provider: str, social_id: str) -> Optional[UserEntity]:
        user = await self.user_repository.get_by_email(email)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.is_active():
            raise HTTPException(status_code=403, detail="User account is disabled")

        if not user.has_social_account(provider) or user.social_accounts[provider] != social_id:
            raise HTTPException(status_code=401, detail=f"Invalid {provider} account")

        user.update_last_login()
        await self.user_repository.update(user)
        
        return user
