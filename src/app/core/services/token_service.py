from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from src.common.exception import (
    InvalidTokenException,
    TokenExpiredException,
    UnauthorizedException
)
from src.app.core.domain.entities.token import TokenEntity
from src.app.core.ports.token_port import TokenRepositoryPort
from icecream import ic

class TokenService:
    def __init__(
        self, 
        token_repository: TokenRepositoryPort,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.token_repository = token_repository
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    async def create_tokens(self, user_id: UUID) -> TokenEntity:
        """새로운 토큰 쌍을 생성합니다."""
        now = datetime.now(timezone.utc)
        
        token_entity = TokenEntity(
            user_id=user_id,
            access_token=self._generate_token(),
            refresh_token=self._generate_token(),
            access_token_expires=now + timedelta(minutes=self.access_token_expire_minutes),
            refresh_token_expires=now + timedelta(days=self.refresh_token_expire_days),
            created_at=now
        )
        
        return await self.token_repository.create(token_entity)

    async def refresh_access_token(self, refresh_token: str) -> TokenEntity:
        """리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급합니다."""
        stored_token = await self.token_repository.get_by_refresh_token(refresh_token)

        ic(stored_token)
        
        if not stored_token:
            raise InvalidTokenException()
            
        if stored_token.is_revoked:
            raise UnauthorizedException()
            
        if stored_token.is_refresh_token_expired():
            raise TokenExpiredException()
            
        # 기존 토큰 무효화
        stored_token.revoke()
        await self.token_repository.create(stored_token)
        
        # 새로운 토큰 생성
        return await self.create_tokens(stored_token.user_id)

    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        """사용자의 모든 토큰을 무효화합니다."""
        await self.token_repository.revoke_all_user_tokens(user_id)

    async def validate_access_token(self, access_token: str) -> TokenEntity:
        """액세스 토큰의 유효성을 검증합니다."""
        token = await self.token_repository.get_by_access_token(access_token)
        
        if not token:
            raise InvalidTokenException()
            
        if not token.is_valid():
            raise TokenExpiredException()
            
        return token

    def _generate_token(self) -> str:
        """실제 구현에서는 JWT 등을 사용하여 토큰을 생성합니다."""
        return str(uuid4())