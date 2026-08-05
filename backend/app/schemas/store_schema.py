from pydantic import BaseModel


class StoreCreate(BaseModel):
    name: str
    location: str
    manager_name: str


class StoreUpdate(BaseModel):
    name: str
    location: str
    manager_name: str


class StoreResponse(BaseModel):
    id: int
    name: str
    location: str
    manager_name: str

    class Config:
        from_attributes = True