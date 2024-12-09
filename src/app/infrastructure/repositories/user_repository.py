from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.app.core.domain.entities.user import UserEntity
from src.app.core.domain.value_objects import UserState
from src.app.core.ports.user_port import UserRepositoryPort
from src.app.adapters.persistence.models.user import UserModel

class UserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserEntity) -> UserEntity:
        db_user = UserModel(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            state=user.state,
            social_accounts=user.social_accounts,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return self._to_entity(db_user)

    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user) if db_user else None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user) if db_user else None

    async def get_by_social_account(self, provider: str, social_id: str) -> Optional[UserEntity]:
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.social_accounts[provider].astext == social_id
            )
        )
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user) if db_user else None

    async def update(self, user: UserEntity) -> UserEntity:
        await self.session.execute(
            update(UserModel)
            .where(UserModel.user_id == user.user_id)
            .values(
                name=user.name,
                email=user.email,
                user_type=user.user_type,
                state=user.state,
                social_accounts=user.social_accounts,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
        )
        await self.session.commit()
        return user

    async def delete(self, user_id: UUID) -> bool:
        result = await self.session.execute(
            delete(UserModel).where(UserModel.user_id == user_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def list_by_state(self, state: UserState) -> List[UserEntity]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.state == state.value)
        )
        return [self._to_entity(db_user) for db_user in result.scalars().all()]

    def _to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            user_id=model.user_id,
            name=model.name,
            email=model.email,
            user_type=model.user_type,
            state=model.state,
            social_accounts=model.social_accounts,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )