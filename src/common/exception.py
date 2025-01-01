# src/common/exception.py
from fastapi import status
from fastapi.responses import JSONResponse

class BaseException(Exception):
    def to_response(self):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": {"message": "Internal Server Error", "type": self.__class__.__name__}}
        )

class EmptyFieldException(BaseException):
    """Required Field Exception"""

    def to_response(self):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": {"message": "필수 필드가 비어 있습니다.", "type": self.__class__.__name__}}
        )


class AuthenticationException(BaseException):
    """Base Authentication Exception"""


class InvalidCredentialsException(AuthenticationException):
    """Invalid username or password"""


class TokenException(AuthenticationException):
    """Base Token Exception"""


class TokenExpiredException(TokenException):
    """Token has expired"""


class InvalidTokenException(TokenException):
    """Token is invalid or malformed"""


class UnauthorizedException(AuthenticationException):
    """User is not authorized to perform this action"""


class PermissionDeniedException(AuthenticationException):
    """User does not have required permissions"""


class AccountLockedException(AuthenticationException):
    """Account has been locked due to multiple failed attempts"""


class AccountDeactivatedException(AuthenticationException):
    """Account has been deactivated"""


class DatabaseConnectionError(BaseException):
    """Database Connection Error"""
