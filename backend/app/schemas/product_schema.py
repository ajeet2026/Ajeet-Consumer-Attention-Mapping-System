from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    brand: str
    price: int
    shelf_id: int


class ProductUpdate(BaseModel):
    name: str
    brand: str
    price: int
    shelf_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    price: int
    shelf_id: int

    class Config:
        from_attributes = True
