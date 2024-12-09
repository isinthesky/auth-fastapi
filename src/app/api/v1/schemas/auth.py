from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

class SocialProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    NAVER = "naver"

class UserType(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"

# Request Models
class LoginRequest(BaseModel):
    email: EmailStr
    provider: SocialProvider
    social_id: str

class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

# Response Models
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expires: datetime
    refresh_token_expires: datetime
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    user_type: UserType
    last_login: datetime
    state: int
    social_accounts: Dict[str, str] = Field(default_factory=dict)
    token: TokenResponse

class GoogleAuthResponse(BaseModel):
    auth_url: str

class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    user_type: UserType
    created_at: datetime
    updated_at: datetime
    last_login: datetime
    state: int
    social_accounts: Dict[str, str] = Field(default_factory=dict)
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

# Error Response Models
class AuthErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())

class TokenErrorDetail(BaseModel):
    code: str
    message: str
    token_type: Optional[str] = None
    expires_at: Optional[datetime] = None

class TokenErrorResponse(BaseModel):
    detail: TokenErrorDetail
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

class AddSocialAccountRequest(BaseModel):
    provider: str
    provider_id: str

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    user_type: str
    state: int
    created_at: datetime
    updated_at: datetime
    last_login: datetime
    social_accounts: Dict[str, str]