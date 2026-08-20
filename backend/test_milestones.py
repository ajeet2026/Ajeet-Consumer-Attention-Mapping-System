import requests
import time

BASE_URL = "http://127.0.0.1:8000"
print("=== Testing Milestone 1 & 2 Endpoints ===\n")

# 1. Test Auth
print("1. Authentication")
try:
    auth_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@retaileye.ai", "password": "admin"})
    if auth_res.status_code == 200:
        token = auth_res.json()["access_token"]
        print("✅ Login successful")
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print(f"❌ Login failed: {auth_res.status_code} {auth_res.text}")
        headers = {}
except Exception as e:
    print(f"❌ Auth error: {e}")
    headers = {}

# 2. Test Configuration (Stores, Cameras, Shelves)
print("\n2. Core Configuration APIs")
endpoints = [
    ("/stores/", "Stores"),
    ("/cameras/", "Cameras"),
    ("/shelves/", "Shelves"),
    ("/products/", "Products")
]

for ep, name in endpoints:
    try:
        res = requests.get(f"{BASE_URL}{ep}", headers=headers)
        if res.status_code == 200:
            print(f"✅ {name} endpoint OK ({len(res.json())} items)")
        else:
            print(f"❌ {name} endpoint failed: {res.status_code}")
    except Exception as e:
         print(f"❌ {name} error: {e}")

# 3. Test Analytics
print("\n3. Analytics APIs")
analytics_endpoints = [
    ("/analytics/live", "Live Stats"),
    ("/analytics/shoppers", "Recent Shoppers"),
    ("/analytics/dwell", "Dwell Stats"),
    ("/analytics/zones", "Zone Stats")
]

for ep, name in analytics_endpoints:
    try:
        res = requests.get(f"{BASE_URL}{ep}", headers=headers)
        if res.status_code == 200:
            print(f"✅ {name} endpoint OK")
        else:
            print(f"❌ {name} endpoint failed: {res.status_code}")
    except Exception as e:
         print(f"❌ {name} error: {e}")

