import sys
import os

# add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.store import Store
from app.models.shelf import Shelf
from app.models.camera import Camera
from app.models.product import Product
from app.models.tracking import TrackingSession, TrackingPoint, ZoneEvent
from app.models.attention import AttentionEvent
from app.models.dwell import DwellEvent, AnalyticsSummary
from app.utils.security import hash_password



def seed_db():
    print("Recreating database tables...")
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS analytics_summaries CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS dwell_events CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS attention_events CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS zone_events CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS tracking_points CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS tracking_sessions CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS products CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS cameras CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS shelves CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS stores CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)



    db = SessionLocal()
    try:
        # 1. Create Admin User
        admin = db.query(User).filter(User.email == "admin@retaileye.ai").first()
        if not admin:
            admin = User(
                name="Admin User",
                email="admin@retaileye.ai",
                password=hash_password("admin123"),
                role="Admin",
            )
            db.add(admin)
            print("Created Admin User: admin@retaileye.ai / admin123")

        # 2. Create Manager User
        manager = (
            db.query(User).filter(User.email == "manager@retaileye.ai").first()
        )
        if not manager:
            manager = User(
                name="Store Manager",
                email="manager@retaileye.ai",
                password=hash_password("manager123"),
                role="Store Manager",
            )
            db.add(manager)
            print("Created Store Manager: manager@retaileye.ai / manager123")

        # 3. Create Stores
        store1 = (
            db.query(Store)
            .filter(Store.name == "Walmart Mall of America")
            .first()
        )
        if not store1:
            store1 = Store(
                name="Walmart Mall of America",
                location="Bloomington, MN",
                manager_name="John Doe",
            )
            db.add(store1)
            db.flush()  # get ID
            print("Created Store: Walmart Mall of America")

        store2 = db.query(Store).filter(Store.name == "Target Downtown").first()
        if not store2:
            store2 = Store(
                name="Target Downtown",
                location="Minneapolis, MN",
                manager_name="Sarah Smith",
            )
            db.add(store2)
            db.flush()
            print("Created Store: Target Downtown")

        # 4. Create Shelves
        if store1:
            shelf1 = (
                db.query(Shelf)
                .filter(
                    Shelf.name == "Beverages Section A1",
                    Shelf.store_id == store1.id,
                )
                .first()
            )
            if not shelf1:
                shelf1 = Shelf(name="Beverages Section A1", store_id=store1.id)
                db.add(shelf1)
                db.flush()
                print("Created Shelf: Beverages Section A1")

            shelf2 = (
                db.query(Shelf)
                .filter(
                    Shelf.name == "Snacks Section B2",
                    Shelf.store_id == store1.id,
                )
                .first()
            )
            if not shelf2:
                shelf2 = Shelf(name="Snacks Section B2", store_id=store1.id)
                db.add(shelf2)
                db.flush()
                print("Created Shelf: Snacks Section B2")

            # 5. Create Cameras
            cam1 = (
                db.query(Camera)
                .filter(
                    Camera.name == "Beverage Cam A1",
                    Camera.store_id == store1.id,
                )
                .first()
            )
            if not cam1:
                cam1 = Camera(
                    name="Beverage Cam A1",
                    ip_address="192.168.1.101",
                    store_id=store1.id,
                )
                db.add(cam1)
                print("Created Camera: Beverage Cam A1")

            cam2 = (
                db.query(Camera)
                .filter(
                    Camera.name == "Snacks Cam B2", Camera.store_id == store1.id
                )
                .first()
            )
            if not cam2:
                cam2 = Camera(
                    name="Snacks Cam B2",
                    ip_address="192.168.1.102",
                    store_id=store1.id,
                )
                db.add(cam2)
                print("Created Camera: Snacks Cam B2")

            # 6. Create Products
            if shelf1:
                prod1 = (
                    db.query(Product)
                    .filter(
                        Product.name == "Coca-Cola 12oz Can",
                        Product.shelf_id == shelf1.id,
                    )
                    .first()
                )
                if not prod1:
                    prod1 = Product(
                        name="Coca-Cola 12oz Can",
                        brand="Coca-Cola",
                        price=2,
                        shelf_id=shelf1.id,
                    )
                    db.add(prod1)
                    print("Created Product: Coca-Cola 12oz Can")

                prod2 = (
                    db.query(Product)
                    .filter(
                        Product.name == "Pepsi 12oz Can",
                        Product.shelf_id == shelf1.id,
                    )
                    .first()
                )
                if not prod2:
                    prod2 = Product(
                        name="Pepsi 12oz Can",
                        brand="PepsiCo",
                        price=2,
                        shelf_id=shelf1.id,
                    )
                    db.add(prod2)
                    print("Created Product: Pepsi 12oz Can")

            if shelf2:
                prod3 = (
                    db.query(Product)
                    .filter(
                        Product.name == "Doritos Nacho Cheese",
                        Product.shelf_id == shelf2.id,
                    )
                    .first()
                )
                if not prod3:
                    prod3 = Product(
                        name="Doritos Nacho Cheese",
                        brand="Frito-Lay",
                        price=4,
                        shelf_id=shelf2.id,
                    )
                    db.add(prod3)
                    print("Created Product: Doritos Nacho Cheese")

            # 7. Create Simulated Shopper Tracking Sessions
            from datetime import datetime, timedelta
            from app.models.tracking import TrackingSession, TrackingPoint, ZoneEvent
            from app.models.attention import AttentionEvent
            from app.models.dwell import DwellEvent

            print("Seeding simulated shopper tracking records...")
            # Session 1: Finished session (shopper walked through the store 1 hour ago)
            t1 = datetime.utcnow() - timedelta(hours=1)
            session1 = TrackingSession(
                camera_id=1,
                tracking_id=101,
                entry_time=t1,
                exit_time=t1 + timedelta(seconds=45),
                duration=45.0
            )
            db.add(session1)
            db.flush() # get ID

            # Points for Session 1
            for offset, (x, y) in enumerate([(100, 150), (140, 160), (200, 200), (280, 220), (320, 250), (450, 300)]):
                pt = TrackingPoint(
                    session_id=session1.id,
                    timestamp=t1 + timedelta(seconds=offset * 7),
                    x_coordinate=float(x),
                    y_coordinate=float(y)
                )
                db.add(pt)

            # Zone events for Session 1
            ze1 = ZoneEvent(
                session_id=session1.id,
                zone_id="Entrance",
                entry_time=t1,
                exit_time=t1 + timedelta(seconds=15),
                duration=15.0
            )
            ze2 = ZoneEvent(
                session_id=session1.id,
                zone_id="Shelf A",
                entry_time=t1 + timedelta(seconds=15),
                exit_time=t1 + timedelta(seconds=35),
                duration=20.0
            )
            ze3 = ZoneEvent(
                session_id=session1.id,
                zone_id="Checkout",
                entry_time=t1 + timedelta(seconds=35),
                exit_time=t1 + timedelta(seconds=45),
                duration=10.0
            )
            db.add(ze1)
            db.add(ze2)
            db.add(ze3)

            # Attention Event & Dwell Event for Session 1 (focussing on beverages Shelf A1)
            if shelf1:
                ae1 = AttentionEvent(
                    session_id=session1.id,
                    shelf_id=shelf1.id,
                    start_time=t1 + timedelta(seconds=18),
                    end_time=t1 + timedelta(seconds=30),
                    duration=12.0
                )
                db.add(ae1)
                de1 = DwellEvent(
                    session_id=session1.id,
                    shelf_id=shelf1.id,
                    duration=12.0
                )
                db.add(de1)

            # Session 2: Another finished session
            t2 = datetime.utcnow() - timedelta(minutes=30)
            session2 = TrackingSession(
                camera_id=1,
                tracking_id=102,
                entry_time=t2,
                exit_time=t2 + timedelta(seconds=60),
                duration=60.0
            )
            db.add(session2)
            db.flush()

            # Points for Session 2
            for offset, (x, y) in enumerate([(110, 160), (220, 180), (390, 120), (410, 130), (450, 150), (480, 260)]):
                pt = TrackingPoint(
                    session_id=session2.id,
                    timestamp=t2 + timedelta(seconds=offset * 10),
                    x_coordinate=float(x),
                    y_coordinate=float(y)
                )
                db.add(pt)

            # Zone events for Session 2
            ze2_1 = ZoneEvent(
                session_id=session2.id,
                zone_id="Entrance",
                entry_time=t2,
                exit_time=t2 + timedelta(seconds=20),
                duration=20.0
            )
            ze2_2 = ZoneEvent(
                session_id=session2.id,
                zone_id="Shelf B",
                entry_time=t2 + timedelta(seconds=20),
                exit_time=t2 + timedelta(seconds=50),
                duration=30.0
            )
            ze2_3 = ZoneEvent(
                session_id=session2.id,
                zone_id="Checkout",
                entry_time=t2 + timedelta(seconds=50),
                exit_time=t2 + timedelta(seconds=60),
                duration=10.0
            )
            db.add(ze2_1)
            db.add(ze2_2)
            db.add(ze2_3)

            # Attention Event & Dwell Event for Session 2 (focussing on snacks Shelf B2)
            if shelf2:
                ae2 = AttentionEvent(
                    session_id=session2.id,
                    shelf_id=shelf2.id,
                    start_time=t2 + timedelta(seconds=25),
                    end_time=t2 + timedelta(seconds=45),
                    duration=20.0
                )
                db.add(ae2)
                de2 = DwellEvent(
                    session_id=session2.id,
                    shelf_id=shelf2.id,
                    duration=20.0
                )
                db.add(de2)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
