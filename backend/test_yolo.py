import cv2
import app.main
from app.ai.detector import ShopperDetector

try:
    detector = ShopperDetector()
    cap = cv2.VideoCapture("/Users/ajeetkumar/Desktop/project/ConsumerAttentionMapping/backend/uploads/108669968.mp4")
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (640, 480))
        # Force YOLO to run without try-except to see the real error
        if detector.model:
            results = detector.model(frame)
            print("YOLO SUCCESS!")
        else:
            print("Model failed to load in init")
except Exception as e:
    import traceback
    traceback.print_exc()
