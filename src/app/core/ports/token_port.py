# app/core/ports/token_port.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.core.domain.entities.token import TokenEntity

class TokenRepositoryPort(ABC):
    @abstractmethod
    async def create(self, token: TokenEntity) -> TokenEntity:
        """토큰 DB에 저장 후 반환"""
        pass

    @abstractmethod
    async def get_by_access_token(self, access_token: str) -> Optional[TokenEntity]:
        """access_token으로 TokenEntity 조회"""
        pass

    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[TokenEntity]:
        """refresh_token으로 TokenEntity 조회"""
        pass

    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        """특정 유저의 토큰을 모두 무효화"""
        pass

    @abstractmethod
    async def cleanup_expired_tokens(self, before_date: datetime) -> int:
        """만료된 토큰들 정리"""
        pass