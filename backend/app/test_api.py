import sys
import os

# add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db, SessionLocal, engine, Base

from app.models.user import User
from app.models.store import Store
from app.models.shelf import Shelf
from app.models.camera import Camera
from app.models.product import Product
from app.utils.security import hash_password


class TestRetailAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We will run tests against a temporary sqlite test database or verify using TestClient on our DB.
        # Since tables are created automatically, we can just use the TestClient.
        cls.client = TestClient(app)

        # Ensure seed users exist in DB
        db = SessionLocal()
        try:
            admin = (
                db.query(User)
                .filter(User.email == "test_admin@retaileye.ai")
                .first()
            )
            if not admin:
                admin = User(
                    name="Test Admin",
                    email="test_admin@retaileye.ai",
                    password=hash_password("admin123"),
                    role="Admin",
                )
                db.add(admin)

            manager = (
                db.query(User)
                .filter(User.email == "test_manager@retaileye.ai")
                .first()
            )
            if not manager:
                manager = User(
                    name="Test Manager",
                    email="test_manager@retaileye.ai",
                    password=hash_password("manager123"),
                    role="Store Manager",
                )
                db.add(manager)
            db.commit()
        finally:
            db.close()

    def login(self, email, password):
        response = self.client.post(
            "/auth/login", data={"username": email, "password": password}
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def test_end_to_end_flow(self):
        # 1. Login as Admin
        admin_token = self.login("test_admin@retaileye.ai", "admin123")
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. Login as Manager
        manager_token = self.login("test_manager@retaileye.ai", "manager123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        # 3. Create Store (Admin only)
        store_response = self.client.post(
            "/stores/",
            json={
                "name": "Test Store Alpha",
                "location": "Miami, FL",
                "manager_name": "Alice Cooper",
            },
            headers=headers,
        )
        self.assertEqual(store_response.status_code, 200)
        store_id = store_response.json()["id"]

        # Try to create store as Manager (should fail because store write requires Admin in our dependency check)
        fail_store = self.client.post(
            "/stores/",
            json={
                "name": "Test Store Fail",
                "location": "NY",
                "manager_name": "Bob",
            },
            headers=manager_headers,
        )
        self.assertEqual(
            fail_store.status_code, 403
        )  # Forbidden for non-Admin

        # 4. Create Shelf (Admin only)
        shelf_response = self.client.post(
            "/shelves/",
            json={"name": "Beverage Shelf T1", "store_id": store_id},
            headers=headers,
        )
        self.assertEqual(shelf_response.status_code, 200)
        shelf_id = shelf_response.json()["id"]

        # 5. Create Product (Admin only)
        product_response = self.client.post(
            "/products/",
            json={
                "name": "Sparkling Water",
                "brand": "LaCroix",
                "price": 3,
                "shelf_id": shelf_id,
            },
            headers=headers,
        )
        self.assertEqual(product_response.status_code, 200)
        product_id = product_response.json()["id"]

        # 6. Create Camera (Admin only)
        camera_response = self.client.post(
            "/cameras/",
            json={
                "name": "Shelf Camera T1",
                "ip_address": "192.168.1.201",
                "store_id": store_id,
            },
            headers=headers,
        )
        self.assertEqual(camera_response.status_code, 200)
        camera_id = camera_response.json()["id"]

        # 7. Verify read permissions (Managers can read stores, shelves, products, cameras)
        stores_list = self.client.get("/stores/", headers=manager_headers)
        self.assertEqual(stores_list.status_code, 200)
        self.assertTrue(any(s["id"] == store_id for s in stores_list.json()))

        shelves_list = self.client.get("/shelves/", headers=manager_headers)
        self.assertEqual(shelves_list.status_code, 200)
        self.assertTrue(any(s["id"] == shelf_id for s in shelves_list.json()))

        cameras_list = self.client.get("/cameras/", headers=manager_headers)
        self.assertEqual(cameras_list.status_code, 200)
        self.assertTrue(any(c["id"] == camera_id for c in cameras_list.json()))

        products_list = self.client.get("/products/", headers=manager_headers)
        self.assertEqual(products_list.status_code, 200)
        self.assertTrue(
            any(p["id"] == product_id for p in products_list.json())
        )

        # 8. Test Simulated Camera Feed Endpoint (Skipped stream read in synchronous test client to prevent thread block)
        pass

        # 8a. Test Video Upload and Registration
        dummy_video = io.BytesIO(b"dummy video data")
        upload_response = self.client.post(
            "/cameras/upload",
            files={"file": ("test_video.mp4", dummy_video, "video/mp4")},
            headers=headers,
        )
        self.assertEqual(upload_response.status_code, 200)
        uploaded_cam_id = upload_response.json()["id"]

        # 8b. Test Analytics API Endpoints
        live_analytics = self.client.get("/analytics/live", headers=headers)
        self.assertEqual(live_analytics.status_code, 200)
        self.assertIn("active_shoppers", live_analytics.json())

        shoppers_list = self.client.get("/analytics/shoppers", headers=headers)
        self.assertEqual(shoppers_list.status_code, 200)

        dwell_stats = self.client.get("/analytics/dwell", headers=headers)
        self.assertEqual(dwell_stats.status_code, 200)

        attention_heatmap = self.client.get("/analytics/attention", headers=headers)
        self.assertEqual(attention_heatmap.status_code, 200)

        zone_stats = self.client.get("/analytics/zones", headers=headers)
        self.assertEqual(zone_stats.status_code, 200)

        # Cleanup uploaded video camera and file
        del_upload = self.client.delete(f"/cameras/{uploaded_cam_id}", headers=headers)
        self.assertEqual(del_upload.status_code, 200)
        uploaded_path = "/Users/ajeetkumar/Desktop/project/ConsumerAttentionMapping/backend/uploads/test_video.mp4"
        if os.path.exists(uploaded_path):
            os.remove(uploaded_path)





        # 9. Cleanup - Delete resources (Admin only)
        del_prod = self.client.delete(f"/products/{product_id}", headers=headers)
        self.assertEqual(del_prod.status_code, 200)

        del_cam = self.client.delete(f"/cameras/{camera_id}", headers=headers)
        self.assertEqual(del_cam.status_code, 200)

        del_shelf = self.client.delete(f"/shelves/{shelf_id}", headers=headers)
        self.assertEqual(del_shelf.status_code, 200)

        del_store = self.client.delete(f"/stores/{store_id}", headers=headers)
        self.assertEqual(del_store.status_code, 200)


if __name__ == "__main__":
    unittest.main()
    # Remove test users
    db = SessionLocal()
    db.query(User).filter(
        User.email.in_(
            ["test_admin@retaileye.ai", "test_manager@retaileye.ai"]
        )
    ).delete(synchronize_session=False)
    db.commit()
    db.close()
