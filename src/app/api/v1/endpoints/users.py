import jwt
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from src.app.api.v1.schemas.auth import (
    CreateUserRequest,
    AddSocialAccountRequest,
    UserResponse
)
from src.app.api.v1.dependencies.user import get_user_service
from src.app.api.v1.schemas.response import create_response, create_error_response
from src.app.api.v1.schemas.common import Response
from src.app.core.services.user_service import UserService
from src.app.core.domain.value_objects import UserState
from src.app.infrastructure.logging.logger import auth_logger
from src.settings.environment import SecretKeyEnvironment

user_router = APIRouter(prefix="/api/v1/users", tags=["users"])

@user_router.post(
    path="",
    response_model=Response[UserResponse],
    summary="새로운 사용자 생성",
    description="새로운 사용자를 생성합니다.",
)
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(get_user_service)
):
    """새로운 사용자를 생성합니다."""
    try:
        user = await user_service.create_user(request.name, request.email)
        return create_response(UserResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            state=user.state,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            social_accounts=user.social_accounts
        ))
    except HTTPException as e:
        auth_logger.error(f"Error creating user: {e.detail}")
        return create_error_response(e.detail, e.status_code)
    except Exception as e:
        auth_logger.error(f"Unexpected error creating user: {e}")
        return create_error_response(str(e), 500)

@user_router.get(
    path="/me",
    response_model=Response[UserResponse],
    summary="사용자 정보 조회",
    description="사용자 정보를 조회합니다.",
)
async def get_me(request: Request):
    """
    쿠키에 있는 access_token을 꺼내어 JWT decode
    사용자 정보(email, name 등)를 반환
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No access token cookie found")

    try:
        payload = jwt.decode(token, 
                             SecretKeyEnvironment.get_secret_key(), 
                             algorithms=[SecretKeyEnvironment.get_algorithm()])
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    # payload 안에 원하는 정보가 들어있다고 가정 (email, name 등)
    user_id = payload.get("sub")      # 구글 id
    email = payload.get("email")
    name = payload.get("name")

    if not user_id or not email:
        raise HTTPException(status_code=400, detail="Token payload incomplete")

    return create_response(
        data={
            "userId": user_id,
            "email": email,
            "name": name
        },
        message="User information retrieved",
        status_code=200
    )

@user_router.get(
    path="/{user_id}",
    response_model=Response[UserResponse],
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
        return create_response(
            data=UserResponse(
                user_id=str(user.user_id),
                name=user.name,
                email=user.email,
                user_type=user.user_type,
                state=user.state,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
                social_accounts=user.social_accounts
            ),
            message="User information retrieved",
            status_code=200
        )
    except HTTPException as e:
        auth_logger.error("Failed to fetch user information", error=str(e))
        raise e
    except Exception as e:
        auth_logger.error("Unexpected error during fetching user information", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    

@user_router.post(
    path="/{user_id}/social-accounts",
    response_model=Response[UserResponse],
    summary="소셜 계정 추가",
    description="사용자에게 소셜 계정을 추가합니다.",
)
async def add_social_account(
    user_id: UUID,
    request: AddSocialAccountRequest,
    user_service: UserService = Depends(get_user_service)
):
    """사용자에게 소셜 계정을 추가합니다."""
    try:
        user = await user_service.add_social_account(user_id, request.provider, request.provider_id)
        return create_response(UserResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            state=user.state,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            social_accounts=user.social_accounts
        ))
    except HTTPException as e:
        auth_logger.error(f"Error adding social account: {e.detail}")
        return create_error_response(e.detail, e.status_code)
    except Exception as e:
        auth_logger.error(f"Unexpected error adding social account: {e}")
        return create_error_response(str(e), 500)

@user_router.patch(
    path="/{user_id}/state",
    response_model=Response[UserResponse],
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
        return create_response(
            data=UserResponse(
                user_id=str(user.user_id),
                name=user.name,
                email=user.email,
                user_type=user.user_type,
                state=user.state,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
                social_accounts=user.social_accounts
            ),
            message="User state changed",
            status_code=200
        )
    except HTTPException as e:
        auth_logger.error("Failed to change user state", error=str(e))
        raise e
    except Exception as e:
        auth_logger.error("Unexpected error during changing user state", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    

@user_router.delete("/{user_id}/social-account/{provider}", response_model=Response[UserResponse])
async def remove_social_account(
    user_id: UUID,
    provider: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자의 소셜 계정을 제거합니다."""
    try:
        user = await user_service.remove_social_account(user_id, provider)
        return create_response(UserResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            user_type=user.user_type,
            state=user.state,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            social_accounts=user.social_accounts
        ))
    except HTTPException as e:
        auth_logger.error(f"Error removing social account: {e.detail}")
        return create_error_response(e.detail, e.status_code)
    except Exception as e:
        auth_logger.error(f"Unexpected error removing social account: {e}")
        return create_error_response(str(e), 500)
    