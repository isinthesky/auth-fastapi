from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.app.core.domain.entities.user import UserEntity
from src.app.core.domain.value_objects import Email, UserState

class UserRepositoryPort(ABC):

    @abstractmethod
    async def create(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def update(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_by_social_account(self, provider: str, social_id: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def list_by_state(self, state: UserState) -> List[UserEntity]:
        pass