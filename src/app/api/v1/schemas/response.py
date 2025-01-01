from datetime import datetime, timezone
from typing import Optional, Any, TypeVar
from src.app.api.v1.schemas.common import Response, ErrorResponse, PaginationResponse

T = TypeVar('T')

def create_response(
    data: Optional[T] = None,
    message: str = "Success",
    status_code: int = 200
) -> Response[T]:
    return Response(
        timestamp=datetime.now(timezone.utc),
        status_code=status_code,
        message=message,
        data=data
    )

def create_error_response(
    message: str,
    error: str,
    status_code: int = 400,
    detail: Optional[Any] = None
) -> ErrorResponse:
    return ErrorResponse(
        timestamp=datetime.now(timezone.utc),
        status_code=status_code,
        message=message,
        error=error,
        detail=detail
    )

def create_pagination_response(
    data: list[T],
    total: int,
    page: int,
    size: int,
    message: str = "Success",
    status_code: int = 200
) -> PaginationResponse[T]:
    total_pages = (total + size - 1) // size
    return PaginationResponse(
        timestamp=datetime.now(timezone.utc),
        status_code=status_code,
        message=message,
        data=data,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    ) 