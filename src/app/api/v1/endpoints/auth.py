from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from src.app.core.ports.auth_port import AuthServicePort
from src.app.api.v1.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    GoogleAuthResponse,
    GoogleAuthRequest,
    CreateUserRequest,
    AddSocialAccountRequest,
    UserResponse
)
from src.app.api.v1.dependencies.auth import get_auth_service
from src.app.api.v1.dependencies.user import get_user_service
from src.app.core.services.user_service import UserService
from src.app.core.domain.value_objects import UserState
from src.app.infrastructure.logging.logger import auth_logger

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post(
    path="/login", 
    response_model=LoginResponse,
    summary="유저 로그인",
    description="유저 로그인",
)
async def login(
    request: LoginRequest,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    auth_logger.info("Login attempt", email=request.email, provider=request.provider)
    try:
        user = await auth_service.login(
            email=request.email,
            provider=request.provider,
            social_id=request.social_id
        )
        auth_logger.info("Login successful", user_id=str(user.user_id))
        return LoginResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            last_login=user.last_login
        )
    except HTTPException as e:
        auth_logger.error("Login failed", error=str(e))
        raise e
    except Exception as e:
        auth_logger.error("Unexpected error during login", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@user_router.get(
    path="/google/auth",
    response_model=GoogleAuthResponse,
    summary="Google OAuth 인증 URL 생성",
    description="Google OAuth 인증을 위한 URL을 생성합니다.",
)
async def google_auth(
    request: Request,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    auth_logger.info("Generating Google OAuth URL")
    try:
        auth_url = await auth_service.get_google_auth_url(
            redirect_uri=str(request.base_url) + "api/v1/users/google/callback"
        )
        auth_logger.info("Google OAuth URL generated", auth_url=auth_url)
        return GoogleAuthResponse(auth_url=auth_url)
    except Exception as e:
        auth_logger.error("Failed to generate Google OAuth URL", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post(
    path="/google/callback",
    response_model=LoginResponse,
    summary="Google OAuth 콜백 처리",
    description="Google OAuth 인증 후 콜백을 처리하고 로그인을 수행합니다.",
)
async def google_callback(
    request: GoogleAuthRequest,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    auth_logger.info("Processing Google OAuth callback", code=request.code)
    try:
        user = await auth_service.google_login(
            auth_code=request.code,
            redirect_uri=request.redirect_uri
        )
        auth_logger.info("Google login successful", user_id=str(user.user_id))
        return LoginResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            last_login=user.last_login
        )
    except HTTPException as e:
        auth_logger.error("Google login failed", error=str(e))
        raise e
    except Exception as e:
        auth_logger.error("Unexpected error during Google login", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    

@user_router.post(
    path="",
    response_model=UserResponse,
    summary="새로운 사용자 생성",
    description="새로운 사용자를 생성합니다.",
)
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(get_user_service)
):
    auth_logger.info("Creating new user", email=request.email)
    try:
        user = await user_service.create_user(
            name=request.name,
            email=request.email
        )
        auth_logger.info("User created successfully", user_id=str(user.user_id))
        return UserResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            state=user.state,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            social_accounts=user.social_accounts
        )
    except HTTPException as e:
        auth_logger.error("User creation failed", error=str(e))
        raise e
    except Exception as e:
        auth_logger.error("Unexpected error during user creation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@user_router.get(
    path="/{user_id}",
    response_model=UserResponse,
    summary="사용자 정보 조회",
    description="사용자 ID로 사용자 정보를 조회합니다.",
)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service)
):
    auth_logger.info("Fetching user information", user_id=str(user_id))
    try:
        user = await user_service.get_user(user_id)
        auth_logger.info("User information retrieved", user_id=str(user.user_id))
        return UserResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            state=user.state,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            social_accounts=user.social_accounts
        )
    except HTTPException as e:
        auth_logger.error("Failed to fetch user information", error=str(e))
        raise e
    except Exception as e:
        auth_logger.error("Unexpected error during fetching user information", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post(
    path="/{user_id}/social-accounts",
    response_model=UserResponse,
    summary="소셜 계정 추가",
    description="사용자에게 소셜 계정을 추가합니다.",
)
async def add_social_account(
    user_id: UUID,
    request: AddSocialAccountRequest,
    user_service: UserService = Depends(get_user_service)
):
    auth_logger.info("Adding social account", user_id=str(user_id), provider=request.provider)
    try:
        user = await user_service.add_social_account(
            user_id=user_id,
            provider=request.provider,
            provider_id=request.provider_id
        )
        auth_logger.info("Social account added", user_id=str(user.user_id))
        return UserResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            state=user.state,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            social_accounts=user.social_accounts
        )
    except HTTPException as e:
        auth_logger.error("Failed to add social account", error=str(e))
        raise e
    except Exception as e:
        auth_logger.error("Unexpected error during adding social account", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@user_router.patch(
    path="/{user_id}/state",
    response_model=UserResponse,
    summary="사용자 상태 변경",
    description="사용자의 상태를 변경합니다.",
)
async def change_user_state(
    user_id: UUID,
    state: UserState,
    user_service: UserService = Depends(get_user_service)
):
    auth_logger.info("Changing user state", user_id=str(user_id), new_state=state.name)
    try:
        user = await user_service.change_user_state(user_id, state)
        auth_logger.info("User state changed", user_id=str(user.user_id), new_state=user.state.name)
        return UserResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            state=user.state,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            social_accounts=user.social_accounts
        )
    except HTTPException as e:
        auth_logger.error("Failed to change user state", error=str(e))
        raise e
    except Exception as e:
        auth_logger.error("Unexpected error during changing user state", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))