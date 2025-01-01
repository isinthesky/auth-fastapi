from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')

class ResponseBase(BaseModel):
    timestamp: datetime
    status_code: int
    message: str
    
class Response(ResponseBase, Generic[T]):
    data: Optional[T] = None
    
class PaginationResponse(Response[T]):
    total: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool

class ErrorResponse(ResponseBase):
    error: str
    detail: Optional[Any] = None