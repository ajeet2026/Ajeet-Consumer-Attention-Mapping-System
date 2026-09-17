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
from app.models.shelf_snapshot import ShelfSnapshot
from app.models.behavior import BehaviorProfile

from app.models.interaction import ProductInteraction
from app.models.scoring import ProductScore

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.admin import router as admin_router
from app.routers.store import router as store_router
from app.routers.shelf import router as shelf_router
from app.routers.camera import router as camera_router
from app.routers.product import router as product_router
from app.routers.analytics import router as analytics_router
from app.routers.behavior import router as behavior_router
from app.routers.analytics_product import router as analytics_product_router
from app.routers.dashboard_router import router as executive_dashboard_router

# Create all database tables
Base.metadata.create_all(bind=engine)

def init_default_data():
    try:
        from app.database.database import SessionLocal
        from app.utils.security import hash_password
        db = SessionLocal()
        if not db.query(User).filter(User.email == "admin@retaileye.ai").first():
            admin = User(
                name="Admin User",
                email="admin@retaileye.ai",
                password=hash_password("admin123"),
                role="Admin",
            )
            db.add(admin)
        if not db.query(User).filter(User.email == "manager@retaileye.ai").first():
            manager = User(
                name="Store Manager",
                email="manager@retaileye.ai",
                password=hash_password("manager123"),
                role="Store Manager",
            )
            db.add(manager)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Startup DB init error: {e}")

init_default_data()

# Create FastAPI app
app = FastAPI(
    title="Consumer Attention Mapping System",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
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

# Behavior Routes
app.include_router(
    behavior_router
)

# Product Analytics Routes
app.include_router(
    analytics_product_router
)

# Executive Role-Based Dashboards
app.include_router(
    executive_dashboard_router
)

# Mount uploads directory for serving shelf snapshots and other static files
from fastapi.staticfiles import StaticFiles
import os
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


# Home Route
@app.get("/")
def home():
    return {
        "message": "Consumer Attention Mapping System"
    }