import urllib.request
from app.database.database import SessionLocal
from app.models.user import User
from app.utils.security import create_access_token

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@retaileye.ai').first()
token = create_access_token({"sub": user.email, "id": user.id, "role": user.role})

url = f"http://127.0.0.1:8000/cameras/17/feed?token={token}"
try:
    with urllib.request.urlopen(url) as response:
        print(f"Status: {response.getcode()}")
        headers = response.getheaders()
        print(headers)
        chunk = response.read(1024) # read 1kb
        print(chunk[:100])
except Exception as e:
    print(f"Error: {e}")
