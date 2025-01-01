from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.domain.entities.user import UserEntity
from src.app.core.domain.value_objects import UserState
from src.app.core.ports.user_port import UserRepositoryPort
from src.app.adapters.persistence.models.user_model import UserModel
from datetime import datetime, timezone
from src.app.adapters.persistence.mappers.user_mapper import UserMapper
from sqlalchemy.dialects.postgresql import JSONB

class UserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = UserMapper()

    async def create(self, user: UserEntity):
        user_model = self.mapper.to_model(user)
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        return self.mapper.to_entity(user_model)

    async def get_by_id(self, user_id: UUID):
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        db_user = result.scalar_one_or_none()
        return self.mapper.to_entity(db_user) if db_user else None

    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()
        return self.mapper.to_entity(db_user) if db_user else None

    async def get_by_social_account(self, provider: str, social_id: str):
        result = await self.session.execute(
            select(UserModel).where(
                cast(UserModel.social_accounts[provider], String) == social_id
            )
        )
        db_user = result.scalar_one_or_none()
        return self.mapper.to_entity(db_user) if db_user else None

    async def update(self, user: UserEntity):
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user.user_id)
        )
        
        db_user = result.scalar_one_or_none()
        if not db_user:
            return None
        
        db_user.name = user.name
        db_user.email = user.email
        db_user.user_type = user.user_type
        db_user.state = user.state
        db_user.social_accounts = user.social_accounts
        db_user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db_user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.session.commit()
        await self.session.refresh(db_user)
        return self.mapper.to_entity(db_user)

    async def delete(self, user_id: UUID):
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        db_user = result.scalar_one_or_none()
        if db_user:
            await self.session.delete(db_user)
            await self.session.commit()
            return True
        return False

    async def list_by_state(self, state: UserState):
        result = await self.session.execute(
            select(UserModel).where(UserModel.state == state.value)
        )
        db_users = result.scalars().all()
        return [self.mapper.to_entity(db_user) for db_user in db_users]