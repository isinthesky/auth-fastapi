from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID
from typing import Dict, Optional
from src.app.core.domain.value_objects import UserState, UserType

@dataclass
class UserEntity:
    user_id: UUID
    name: str
    email: str
    user_type: str
    created_at: datetime
    updated_at: datetime
    last_login: datetime
    state: int
    social_accounts: Dict[str, str] = field(default_factory=dict)  

    def is_active(self) -> bool:
        """사용자가 활성 상태인지 확인합니다."""
        return self.state == UserState.ACTIVE.value

    def is_hidden(self) -> bool:
        """사용자가 숨김 상태인지 확인합니다."""
        return self.state == UserState.HIDDEN.value

    def is_disabled(self) -> bool:
        """사용자가 비활성화 상태인지 확인합니다."""
        return self.state == UserState.DISABLED.value

    def update_last_login(self) -> None:
        """마지막 로그인 시간을 갱신합니다."""
        self.last_login = datetime.now(timezone.utc)

    def add_social_account(self, provider: str, provider_id: str) -> None:
        """소셜 계정 정보를 추가합니다."""
        self.social_accounts[provider] = provider_id
        self.updated_at = datetime.now(timezone.utc)
        self.last_login = datetime.now(timezone.utc)

    def remove_social_account(self, provider: str) -> None:
        """소셜 계정 정보를 제거합니다."""
        if provider in self.social_accounts:
            del self.social_accounts[provider]

    def change_state(self, new_state: UserState) -> None:
        """사용자 상태를 변경합니다."""
        self.state = new_state.value

    def has_social_account(self, provider: str) -> bool:
        """특정 제공자의 소셜 계정이 있는지 확인합니다."""
        return provider in self.social_accounts

    @property
    def is_admin(self) -> bool:
        """관리자 권한을 가지고 있는지 확인합니다."""
        return self.user_type == UserType.ADMIN.value

    @property
    def google_id(self) -> Optional[str]:
        return self.social_accounts.get("google")

    @property
    def facebook_id(self) -> Optional[str]:
        return self.social_accounts.get("facebook")

    @property
    def naver_id(self) -> Optional[str]:
        return self.social_accounts.get("naver")
    