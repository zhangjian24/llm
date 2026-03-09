"""
通用 Schema
"""
from typing import List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class PageDTO(BaseModel, Generic[T]):
    """分页响应 DTO"""
    total: int
    items: List[T]
    page: int
    limit: int
    total_pages: int


class SuccessResponse(BaseModel, Generic[T]):
    """统一成功响应"""
    code: int = 0
    message: str = "success"
    data: T
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "success",
                "data": {}
            }
        }
