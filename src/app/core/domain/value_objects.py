from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

class UserState(Enum):
    DISABLED = 0
    ACTIVE = 1
    HIDDEN = 2

class UserType(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"


@dataclass(frozen=True)
class SocialAccountInfo:
    provider_id: str
    provider_type: str  # "google", "facebook", "naver"


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not '@' in self.value:
            raise ValueError("Invalid email format")

@dataclass(frozen=True)
class TokenPayload:
    sub: str
    exp: datetime
    token_type: str
