from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine, Base

from app.models.user import User
from app.models.store import Store
from app.models.shelf import Shelf
from app.models.product import Product
from app.models.camera import Camera
from app.models.tracking import TrackingSession, TrackingPoint, ZoneEvent
from app.models.attention import AttentionEvent
from app.models.dwell import DwellEvent, AnalyticsSummary

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.admin import router as admin_router
from app.routers.store import router as store_router
from app.routers.shelf import router as shelf_router
from app.routers.camera import router as camera_router
from app.routers.product import router as product_router
from app.routers.analytics import router as analytics_router

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Consumer Attention Mapping System",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Routes
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

# User Routes
app.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

# Admin Routes
app.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"]
)

# Store Routes
app.include_router(
    store_router
)

# Shelf Routes
app.include_router(
    shelf_router
)

# Camera Routes
app.include_router(
    camera_router
)

# Product Routes
app.include_router(
    product_router
)

# Analytics Routes
app.include_router(
    analytics_router
)


# Home Route
@app.get("/")
def home():
    return {
        "message": "Consumer Attention Mapping System"
    }