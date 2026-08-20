import sys
import traceback
import app.main
from app.routers.camera import generate_frames_cv2

try:
    print("Initializing generator...")
    gen = generate_frames_cv2(17, "Test Camera", "/Users/ajeetkumar/Desktop/project/ConsumerAttentionMapping/backend/uploads/My Movie 2.mp4")
    print("Fetching frame...")
    chunk = next(gen)
    print(f"Success! Chunk size: {len(chunk)}")
except Exception as e:
    traceback.print_exc()
