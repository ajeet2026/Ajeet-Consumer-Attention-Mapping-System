import cv2
import numpy as np
import os
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

model_path = "app/ai/face_landmarker.task"
base_options = mp_python.BaseOptions(model_asset_path=model_path)
options = mp_vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=mp_vision.RunningMode.IMAGE,
    num_faces=5,
    min_face_detection_confidence=0.3,
    min_face_presence_confidence=0.3,
)
landmarker = mp_vision.FaceLandmarker.create_from_options(options)
print("FaceLandmarker initialized!")

cap = cv2.VideoCapture("uploads/108669968.mp4")
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
test_positions = [int(total_frames * i / 10) for i in range(10)]

faces_found = 0
frames_tested = 0

for pos in test_positions:
    cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (640, 480))
    frames_tested += 1

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results = landmarker.detect(mp_image)

    if results.face_landmarks and len(results.face_landmarks) > 0:
        faces_found += 1
        num_faces = len(results.face_landmarks)
        print(f"Frame {pos}: FOUND {num_faces} face(s)")
    else:
        print(f"Frame {pos}: No faces detected")

cap.release()
print(f"\nSummary: Found faces in {faces_found}/{frames_tested} frames tested")
