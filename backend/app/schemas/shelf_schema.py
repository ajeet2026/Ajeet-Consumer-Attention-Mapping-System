from pydantic import BaseModel
from typing import Optional


class ShelfCreate(BaseModel):
    name: str
    store_id: int
    bbox_x1: Optional[int] = None
    bbox_y1: Optional[int] = None
    bbox_x2: Optional[int] = None
    bbox_y2: Optional[int] = None


class ShelfUpdate(BaseModel):
    name: str
    store_id: int
    bbox_x1: Optional[int] = None
    bbox_y1: Optional[int] = None
    bbox_x2: Optional[int] = None
    bbox_y2: Optional[int] = None


class ShelfResponse(BaseModel):
    id: int
    name: str
    store_id: int
    bbox_x1: Optional[int] = None
    bbox_y1: Optional[int] = None
    bbox_x2: Optional[int] = None
    bbox_y2: Optional[int] = None

    class Config:
        from_attributes = True

