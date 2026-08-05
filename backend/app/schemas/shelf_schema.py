from pydantic import BaseModel


class ShelfCreate(BaseModel):
    name: str
    store_id: int


class ShelfUpdate(BaseModel):
    name: str
    store_id: int


class ShelfResponse(BaseModel):
    id: int
    name: str
    store_id: int

    class Config:
        from_attributes = True
