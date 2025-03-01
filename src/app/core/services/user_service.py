from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from fastapi import HTTPException
from src.app.core.domain.entities.user import UserEntity
from src.app.core.domain.value_objects import UserState, UserType
from src.app.core.ports.user_port import UserRepositoryPort
from icecream import ic

class UserService:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    async def create_user(self, name: str, email: str) -> UserEntity:
        """새로운 사용자를 생성합니다."""
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        now = datetime.now(timezone.utc)
        user = UserEntity(
            user_id=uuid4(),
            name=name,
            email=email,
            user_type=UserType.USER.value,
            created_at=now,
            updated_at=now,
            last_login=now,
            state=UserState.ACTIVE.value,
            social_accounts={}
        )

        return await self.user_repository.create(user)
    

    async def change_user_state(self, user_id: UUID, state: UserState) -> UserEntity:
        """사용자의 상태를 변경합니다."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.change_state(state)
        return await self.user_repository.update(user)

    async def add_social_account(self, user_id: UUID, provider: str, provider_id: str) -> UserEntity:
        """사용자의 소셜 계정을 추가합니다."""
        # 기존 소셜 계정 확인
        existing_user = await self.user_repository.get_by_social_account(provider, provider_id)

        ic("add_social_account", existing_user)

        if existing_user and existing_user.user_id != user_id:
            raise HTTPException(status_code=400, detail=f"This {provider} account is already linked to another user")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        ic("add_social_account get_by_id", user)

        user.add_social_account(provider, provider_id)

        ic("add_social_account user", user)

        return await self.user_repository.update(user)
    
    async def has_social_account(self, user_id: UUID, provider: str) -> bool:
        """사용자가 특정 소셜 계정을 가지고 있는지 확인합니다."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user.has_social_account(provider)

    async def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        """이메일로 사용자를 조회합니다."""
        return await self.user_repository.get_by_email(email)
    
    async def get_user_by_id(self, user_id: UUID) -> UserEntity:
        """사용자 ID로 사용자를 조회합니다."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def remove_social_account(self, user_id: UUID, provider: str) -> UserEntity:
        """사용자의 소셜 계정을 제거합니다."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.remove_social_account(provider)
        return await self.user_repository.update(user)
