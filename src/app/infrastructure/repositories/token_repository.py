from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.app.core.domain.entities.token import TokenEntity
from src.app.core.ports.token_port import TokenRepositoryPort
from src.app.adapters.persistence.models.token import TokenModel

class TokenRepository(TokenRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: TokenEntity) -> TokenEntity:
        db_token = TokenModel(
            user_id=token.user_id,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            access_token_expires=token.access_token_expires,
            refresh_token_expires=token.refresh_token_expires,
            is_revoked=token.is_revoked,
            created_at=token.created_at,
            revoked_at=token.revoked_at
        )
        self.session.add(db_token)
        await self.session.commit()
        await self.session.refresh(db_token)
        return self._to_entity(db_token)

    async def get_by_access_token(self, access_token: str) -> Optional[TokenEntity]:
        result = await self.session.execute(
            select(TokenModel).where(TokenModel.access_token == access_token)
        )
        db_token = result.scalar_one_or_none()
        return self._to_entity(db_token) if db_token else None

    async def get_by_refresh_token(self, refresh_token: str) -> Optional[TokenEntity]:
        result = await self.session.execute(
            select(TokenModel).where(TokenModel.refresh_token == refresh_token)
        )
        db_token = result.scalar_one_or_none()
        return self._to_entity(db_token) if db_token else None

    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        await self.session.execute(
            update(TokenModel)
            .where(TokenModel.user_id == user_id)
            .values(
                is_revoked=True,
                revoked_at=datetime.now(timezone.utc)
            )
        )
        await self.session.commit()

    async def cleanup_expired_tokens(self, before_date: datetime) -> int:
        result = await self.session.execute(
            delete(TokenModel).where(
                (TokenModel.access_token_expires < before_date) &
                (TokenModel.refresh_token_expires < before_date)
            )
        )
        await self.session.commit()
        return result.rowcount

    def _to_entity(self, model: TokenModel) -> TokenEntity:
        return TokenEntity(
            user_id=model.user_id,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
            access_token_expires=model.access_token_expires,
            refresh_token_expires=model.refresh_token_expires,
            is_revoked=model.is_revoked,
            created_at=model.created_at,
            revoked_at=model.revoked_at
        )