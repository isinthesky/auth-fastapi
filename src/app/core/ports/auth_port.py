from abc import ABC, abstractmethod
from typing import Optional
from ..domain.entities.user import UserEntity
from ..domain.entities.token import TokenEntity

class AuthServicePort(ABC):
    @abstractmethod
    async def login(self, email: str, provider: str, social_id: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def create_tokens(self, user: UserEntity) -> TokenEntity:
        pass 

    @abstractmethod
    async def get_google_auth_url(self, redirect_uri: str) -> str:
        pass

    @abstractmethod
    async def google_login(self, auth_code: str, redirect_uri: str) -> Optional[UserEntity]:
        pass
    