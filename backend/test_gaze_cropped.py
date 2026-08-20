import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from ultralytics import YOLO

# Init YOLO
yolo = YOLO("yolov8n.pt")

# Init FaceLandmarker
model_path = "app/ai/face_landmarker.task"
base_options = mp_python.BaseOptions(model_asset_path=model_path)
options = mp_vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=mp_vision.RunningMode.IMAGE,
    num_faces=5,
    min_face_detection_confidence=0.2,
    min_face_presence_confidence=0.2,
)
landmarker = mp_vision.FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture("uploads/108669968.mp4")
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
test_positions = [int(total_frames * i / 10) for i in range(10)]

total_persons = 0
faces_in_crops = 0

for pos in test_positions:
    cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.resize(frame, (640, 480))
    
    # YOLO detect persons
    results = yolo(frame, verbose=False)
    for r in results:
        for box in r.boxes:
            if int(box.cls[0]) == 0:  # person
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                total_persons += 1
                
                # Crop person bbox
                crop = frame[max(0,y1):min(480,y2), max(0,x1):min(640,x2)]
                h, w = crop.shape[:2]
                print(f"  Frame {pos}: Person crop size {w}x{h}", end="")
                
                rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_crop)
                face_results = landmarker.detect(mp_image)
                
                if face_results.face_landmarks and len(face_results.face_landmarks) > 0:
                    faces_in_crops += 1
                    print(f" -> FACE FOUND!")
                else:
                    print(f" -> no face")

cap.release()
print(f"\nSummary: Found faces in {faces_in_crops}/{total_persons} person crops")
