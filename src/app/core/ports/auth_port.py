# app/core/ports/auth_port.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.core.domain.entities.token import TokenEntity

class AuthServicePort(ABC):
    @abstractmethod
    async def login(self, email: str, provider: str, social_id: str) -> UUID:
        """
        로그인 후, 사용자 식별자(또는 UserEntity)를 반환.
        소셜 로그인 기반으로 예시.
        """
        pass

    @abstractmethod
    async def create_tokens(self, user_id: UUID) -> TokenEntity:
        """
        유저 ID를 받아 토큰 엔티티를 생성/저장하고 반환.
        """
        pass
    
    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> TokenEntity:
        """
        리프레시 토큰을 사용해 새로운 액세스 토큰 생성/반환.
        """
        pass

    @abstractmethod
    async def validate_access_token(self, access_token: str) -> TokenEntity:
        """
        액세스 토큰의 유효성을 검증.
        유효하면 TokenEntity 반환, 아니면 예외 발생.
        """
        pass