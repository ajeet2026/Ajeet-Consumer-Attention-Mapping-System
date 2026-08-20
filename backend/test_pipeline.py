import app.main
from app.ai.detector import ShopperDetector
from app.ai.gaze import GazeEstimator
from app.ai.attention import AttentionDetector
import cv2

print("=== Testing Full Pipeline ===\n")

# 1. Test YOLO Detection
print("1. Person Detection (YOLOv8):")
detector = ShopperDetector()
if detector.model:
    print("   ✅ YOLO model loaded successfully")
else:
    print("   ❌ YOLO model failed to load")

cap = cv2.VideoCapture("uploads/108669968.mp4")
ret, frame = cap.read()
frame = cv2.resize(frame, (640, 480))
detections = detector.detect(frame)
print(f"   Detected {len(detections)} real persons")
if len(detections) == 0:
    print("   Testing with no persons: returns empty list (no faking)")

# 2. Test with None frame (should return empty, not simulated)
empty_dets = detector.detect(None)
print(f"   Null frame test: {len(empty_dets)} detections (should be 0, no simulation)")

# 3. Test Gaze Estimation
print("\n2. Gaze Estimation (MediaPipe FaceLandmarker v1.0):")
gaze = GazeEstimator()
if gaze.landmarker:
    print("   ✅ FaceLandmarker initialized")
else:
    print("   ⚠️ FaceLandmarker not available")

if len(detections) > 0:
    bbox = detections[0]["bbox"]
    result = gaze.estimate_gaze(frame, bbox, tracker_id=1)
    print(f"   Gaze result: direction={result['direction']}, yaw={result['yaw']:.1f}, pitch={result['pitch']:.1f}")
    print(f"   Vector: {[round(v, 3) for v in result['gaze_vector']]}")

# 4. Test Attention Detection
print("\n3. Attention Detection (Ray-Box Intersection):")
attention = AttentionDetector()
if len(detections) > 0:
    bbox = detections[0]["bbox"]
    cx = (bbox[0] + bbox[2]) // 2
    cy = (bbox[1] + bbox[3]) // 2
    gaze_vec = result["gaze_vector"]
    shelf_id = attention.detect_attention((cx, cy), gaze_vec)
    print(f"   Shopper at ({cx},{cy}) with gaze {[round(v,2) for v in gaze_vec]} -> Shelf: {shelf_id}")

cap.release()
print("\n=== Pipeline Test Complete ===")
