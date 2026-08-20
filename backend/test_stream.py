from app.database.database import SessionLocal
from app.models.user import User
from app.utils.security import create_access_token
import urllib.request

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@retaileye.ai').first()
token = create_access_token({"sub": user.email, "id": user.id, "role": user.role})

url = "http://127.0.0.1:8000/cameras/1/video_feed"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.getcode()}")
        for _ in range(5):
            print(response.readline())
except Exception as e:
    print(f"Error: {e}")
