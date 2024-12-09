from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

@dataclass
class TokenEntity:
    user_id: UUID
    access_token: str
    refresh_token: str
    access_token_expires: datetime
    refresh_token_expires: datetime
    is_revoked: bool = False
    created_at: datetime = datetime.now(timezone.utc)
    revoked_at: Optional[datetime] = None

    def revoke(self) -> None:
        """토큰을 폐기 상태로 만듭니다."""
        self.is_revoked = True
        self.revoked_at = datetime.now(timezone.utc)

    def is_access_token_expired(self) -> bool:
        """액세스 토큰이 만료되었는지 확인합니다."""
        return datetime.now(timezone.utc) > self.access_token_expires

    def is_refresh_token_expired(self) -> bool:
        """리프레시 토큰이 만료되었는지 확인합니다."""
        return datetime.now(timezone.utc) > self.refresh_token_expires

    def is_valid(self) -> bool:
        """토큰이 유효한 상태인지 확인합니다."""
        return (not self.is_revoked and 
                not self.is_access_token_expired() and 
                not self.is_refresh_token_expired())
