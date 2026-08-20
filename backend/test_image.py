import cv2
import app.main
from app.routers.camera import generate_frames_cv2

gen = generate_frames_cv2(17, "Test Camera", "/Users/ajeetkumar/Desktop/project/ConsumerAttentionMapping/backend/uploads/My Movie 2.mp4")
chunk = next(gen)
# Extract just the JPEG bytes from the multipart chunk
# b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
parts = chunk.split(b'\r\n\r\n')
if len(parts) > 1:
    jpeg_bytes = parts[1][:-2] # remove trailing \r\n
    with open("test_frame.jpg", "wb") as f:
        f.write(jpeg_bytes)
    print("Saved test_frame.jpg")
