import math
import os
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    HAS_MP = True
except ImportError:
    HAS_MP = False


class GazeEstimator:
    """
    Real gaze estimator using MediaPipe FaceLandmarker v1.0 + OpenCV solvePnP.

    Extracts 478 facial landmarks from the detected person's bounding box crop,
    then uses 6 key points (nose, chin, eyes, mouth corners) to solve
    the Perspective-n-Point problem and compute the true 3D head rotation
    matrix (pitch, yaw, roll).

    If a face cannot be detected (e.g., person facing away, too far from camera),
    it returns a neutral "Looking Forward" gaze rather than faking data.
    """

    def __init__(self):
        self.landmarker = None
        if HAS_MP and HAS_CV2:
            try:
                model_path = os.path.join(
                    os.path.dirname(__file__), "face_landmarker.task"
                )
                if os.path.exists(model_path):
                    base_options = mp_python.BaseOptions(
                        model_asset_path=model_path
                    )
                    options = mp_vision.FaceLandmarkerOptions(
                        base_options=base_options,
                        running_mode=mp_vision.RunningMode.IMAGE,
                        num_faces=5,
                        min_face_detection_confidence=0.3,
                        min_face_presence_confidence=0.3,
                        min_tracking_confidence=0.3,
                    )
                    self.landmarker = mp_vision.FaceLandmarker.create_from_options(options)
                    print("MediaPipe FaceLandmarker v1.0 initialized successfully.")
                else:
                    print(f"FaceLandmarker model not found at: {model_path}")
            except Exception as e:
                print(f"Failed to initialize MediaPipe FaceLandmarker: {e}")

    def estimate_gaze(self, frame, bbox, tracker_id=None):
        """
        Estimates head pose (pitch, yaw, roll) and gaze vector.

        Uses MediaPipe FaceLandmarker to extract real facial geometry,
        then OpenCV solvePnP to compute the 3D rotation matrix.

        If face is not detected, returns neutral forward gaze (no simulation).

        Returns a dict: {"pitch", "yaw", "roll", "gaze_vector", "direction"}
        """
        # Try real face landmark detection + solvePnP
        if self.landmarker and frame is not None and HAS_CV2:
            try:
                h, w, _ = frame.shape
                x1, y1, x2, y2 = bbox
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                if x2 > x1 and y2 > y1:
                    crop_h, crop_w = y2 - y1, x2 - x1

                    # Skip crops too small for face detection
                    if crop_w >= 40 and crop_h >= 40:
                        crop = frame[y1:y2, x1:x2]
                        rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                        mp_image = mp.Image(
                            image_format=mp.ImageFormat.SRGB, data=rgb_crop
                        )
                        results = self.landmarker.detect(mp_image)

                        if results.face_landmarks and len(results.face_landmarks) > 0:
                            landmarks = results.face_landmarks[0]

                            # Extract 2D image points from 478 facial landmarks
                            # Key points: Nose(1), Chin(152), Left Eye(33),
                            # Right Eye(263), Left Mouth(61), Right Mouth(291)
                            face_2d = []
                            for idx in [1, 152, 33, 263, 61, 291]:
                                lm = landmarks[idx]
                                face_2d.append([lm.x * crop_w, lm.y * crop_h])

                            face_2d = np.array(face_2d, dtype=np.float64)

                            # 3D generic anthropometric face model
                            face_3d = np.array([
                                (0.0, 0.0, 0.0),            # Nose tip
                                (0.0, 330.0, -65.0),         # Chin
                                (225.0, -170.0, -135.0),     # Left eye
                                (-225.0, -170.0, -135.0),    # Right eye
                                (150.0, 150.0, -125.0),      # Left Mouth
                                (-150.0, 150.0, -125.0)      # Right Mouth
                            ], dtype=np.float64)

                            # Camera intrinsics approximation
                            focal_length = crop_w
                            cam_matrix = np.array([
                                [focal_length, 0, crop_w / 2],
                                [0, focal_length, crop_h / 2],
                                [0, 0, 1]
                            ], dtype=np.float64)
                            dist_matrix = np.zeros((4, 1), dtype=np.float64)

                            # Solve PnP — compute real 3D rotation
                            success, rot_vec, trans_vec = cv2.solvePnP(
                                face_3d, face_2d, cam_matrix, dist_matrix
                            )

                            if success:
                                rmat, _ = cv2.Rodrigues(rot_vec)
                                angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

                                pitch = float(angles[0])
                                yaw = float(angles[1])
                                roll = float(angles[2])

                                yaw_rad = math.radians(yaw)
                                pitch_rad = math.radians(pitch)

                                x_vec = math.sin(yaw_rad) * math.cos(pitch_rad)
                                y_vec = math.sin(pitch_rad)
                                z_vec = math.cos(yaw_rad) * math.cos(pitch_rad)

                                if yaw < -12:
                                    direction = "Looking Left"
                                elif yaw > 12:
                                    direction = "Looking Right"
                                elif pitch > 10:
                                    direction = "Looking Down"
                                elif pitch < -10:
                                    direction = "Looking Up"
                                else:
                                    direction = "Looking Forward"

                                return {
                                    "pitch": pitch,
                                    "yaw": yaw,
                                    "roll": roll,
                                    "gaze_vector": [x_vec, y_vec, z_vec],
                                    "direction": direction,
                                }

            except Exception as e:
                print(f"MediaPipe processing error: {e}")

        # Face not detected — return neutral forward gaze (no simulation)
        return {
            "pitch": 0.0,
            "yaw": 0.0,
            "roll": 0.0,
            "gaze_vector": [0.0, 0.0, 1.0],
            "direction": "Looking Forward",
        }
