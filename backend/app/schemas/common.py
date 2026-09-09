from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = 1
    size: int = 50

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class SuccessResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
