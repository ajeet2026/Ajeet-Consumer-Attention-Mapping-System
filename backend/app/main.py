from fastapi import FastAPI

from app.database.database import engine
from app.database.database import Base

from app.models.user import User
from app.models.store import Store
from app.models.shelf import Shelf
from app.models.product import Product
from app.models.camera import Camera
from app.routers.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


@app.get("/")
def home():
    return {
        "message": "Consumer Attention Mapping System"
    }