# src/common/exception_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse
from src.common.exception import (
    BaseException,
    EmptyFieldException,
    AuthenticationException,
    InvalidCredentialsException,
    TokenException,
    TokenExpiredException,
    InvalidTokenException,
    UnauthorizedException,
    PermissionDeniedException,
    AccountLockedException,
    AccountDeactivatedException,
    DatabaseConnectionError
)
import logging

logger = logging.getLogger(__name__)

def exception_handler(request: Request, exc: BaseException):
    """
    중앙 집중식 예외 핸들러
    """
    logger.error(f"Exception occurred: {exc}", exc_info=True)
    
    # 예외 타입에 따라 상태 코드와 메시지 설정
    if isinstance(exc, EmptyFieldException):
        status_code = 400
        detail = "필수 필드가 비어 있습니다."
    elif isinstance(exc, InvalidCredentialsException):
        status_code = 401
        detail = "잘못된 사용자 이름 또는 비밀번호입니다."
    elif isinstance(exc, TokenExpiredException):
        status_code = 401
        detail = "토큰이 만료되었습니다."
    elif isinstance(exc, InvalidTokenException):
        status_code = 401
        detail = "토큰이 유효하지 않거나 형식이 잘못되었습니다."
    elif isinstance(exc, UnauthorizedException):
        status_code = 403
        detail = "이 작업을 수행할 권한이 없습니다."
    elif isinstance(exc, PermissionDeniedException):
        status_code = 403
        detail = "필요한 권한이 없습니다."
    elif isinstance(exc, AccountLockedException):
        status_code = 403
        detail = "여러 번의 실패 시도로 인해 계정이 잠겼습니다."
    elif isinstance(exc, AccountDeactivatedException):
        status_code = 403
        detail = "계정이 비활성화되었습니다."
    elif isinstance(exc, DatabaseConnectionError):
        status_code = 500
        detail = "데이터베이스 연결 오류가 발생했습니다."
    else:
        # 기본적으로 500 에러 반환
        status_code = 500
        detail = "내부 서버 오류가 발생했습니다."

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": detail,
                "type": exc.__class__.__name__
            }
        }
    )