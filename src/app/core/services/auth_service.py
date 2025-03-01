# app/core/services/auth_service.py
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.core.domain.entities.token import TokenEntity
from app.core.ports.token_port import TokenRepositoryPort
from app.core.ports.auth_port import AuthServicePort

class AuthService(AuthServicePort):
    def __init__(self, token_repository: TokenRepositoryPort):
        self.token_repository = token_repository

        # 토큰 만료 시간 설정 (예시)
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    async def login(self, email: str, provider: str, social_id: str) -> UUID:
        """
        1) userRepository에서 user를 찾는다 (user가 없으면 예외)
        2) 소셜계정(provider, social_id) 검증
        3) 로그인 성공 시 user_id 반환
        """
        # 실제로는 userRepository 등으로 user 조회
        # 아래는 예시 - DB검증 스킵
        if not email or not social_id:
            raise HTTPException(status_code=400, detail="Invalid social login")

        # user_id를 가져왔다고 가정
        user_id = UUID("11111111-1111-1111-1111-111111111111")
        return user_id

    async def create_tokens(self, user_id: UUID) -> TokenEntity:
        now = datetime.now(timezone.utc)
        access_token_expires = now + timedelta(minutes=self.access_token_expire_minutes)
        refresh_token_expires = now + timedelta(days=self.refresh_token_expire_days)

        # 실제 구현에서는 JWT를 생성하거나 UUID등을 생성해도 됨
        access_token = f"access-{user_id}-{int(now.timestamp())}"
        refresh_token = f"refresh-{user_id}-{int(now.timestamp())}"

        token_entity = TokenEntity(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires=access_token_expires,
            refresh_token_expires=refresh_token_expires,
            created_at=now,
            is_revoked=False,
        )

        # 토큰 DB 저장
        return await self.token_repository.create(token_entity)

    async def refresh_access_token(self, refresh_token: str) -> TokenEntity:
        stored_token = await self.token_repository.get_by_refresh_token(refresh_token)

        if not stored_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        if stored_token.is_revoked or stored_token.is_refresh_token_expired():
            raise HTTPException(status_code=401, detail="Refresh token expired or revoked")

        # 기존 토큰 무효화
        stored_token.revoke()
        await self.token_repository.create(stored_token)  # 새로 저장(상태 갱신)

        # 새 토큰 발급
        return await self.create_tokens(stored_token.user_id)

    async def validate_access_token(self, access_token: str) -> TokenEntity:
        token = await self.token_repository.get_by_access_token(access_token)
        if not token or not token.is_valid():
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return token