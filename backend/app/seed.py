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
from app.utils.security import hash_password


def seed_db():
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
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

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
