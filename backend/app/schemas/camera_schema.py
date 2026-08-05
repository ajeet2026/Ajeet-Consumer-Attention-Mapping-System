from pydantic import BaseModel


class CameraCreate(BaseModel):
    name: str
    ip_address: str
    store_id: int


class CameraUpdate(BaseModel):
    name: str
    ip_address: str
    store_id: int


class CameraResponse(BaseModel):
    id: int
    name: str
    ip_address: str
    store_id: int

    class Config:
        from_attributes = True
