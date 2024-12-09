from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from uuid import UUID
from src.app.core.domain.entities.token import TokenEntity

class TokenRepositoryPort(ABC):
    @abstractmethod
    async def create(self, token: TokenEntity) -> TokenEntity:
        pass

    @abstractmethod
    async def get_by_access_token(self, access_token: str) -> Optional[TokenEntity]:
        pass

    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[TokenEntity]:
        pass

    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def cleanup_expired_tokens(self, before_date: datetime) -> int:
        pass