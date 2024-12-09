class BaseException(Exception): ...


class EmptyFieldException(BaseException):
    """Required Field Exception"""


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
