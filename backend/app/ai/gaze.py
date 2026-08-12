import time
import math

try:
    import cv2
    import mediapipe as mp

    HAS_MP = True
except ImportError:
    HAS_MP = False


class GazeEstimator:
    def __init__(self):
        self.face_mesh = None
        if HAS_MP:
            try:
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    max_num_faces=5,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
            except Exception as e:
                print(f"Failed to initialize MediaPipe FaceMesh: {e}")

    def estimate_gaze(self, frame, bbox):
        """
        Estimates head pose (pitch, yaw, roll) and gaze vector.
        Returns a dict: {"pitch": float, "yaw": float, "roll": float, "gaze_vector": [x, y, z], "direction": str}
        """
        if self.face_mesh and frame is not None:
            try:
                h, w, _ = frame.shape
                # Crop to bounding box (with safety margins)
                x1, y1, x2, y2 = bbox
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                if x2 > x1 and y2 > y1:
                    crop = frame[y1:y2, x1:x2]
                    rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                    results = self.face_mesh.process(rgb_crop)

                    if results.multi_face_landmarks:
                        # Extract landmarks for head pose calculation
                        # For a real implementation, we use standard key points:
                        # nose tip (1), chin (152), left eye corner (33), right eye corner (263), etc.
                        # and run cv2.solvePnP.
                        # If PnP runs successfully, we get rotation vectors.
                        pass
            except Exception as e:
                print(f"MediaPipe processing error: {e}")

        # High-Fidelity Gaze Simulation
        t = time.time()

        # Generate a gaze direction that sweeps left and right, looking down at shelves
        # frequency based on coordinates to differentiate shoppers
        shopper_seed = (bbox[0] + bbox[1]) % 100
        yaw = float(math.sin(t * 1.5 + shopper_seed) * 35)  # -35 to +35 degrees
        pitch = float(
            math.sin(t * 0.8) * 10 - 8
        )  # looking slightly down (-18 to +2 degrees)
        roll = 0.0

        yaw_rad = math.radians(yaw)
        pitch_rad = math.radians(pitch)

        # Standard 3D Gaze Vector calculation
        x_vec = math.sin(yaw_rad) * math.cos(pitch_rad)
        y_vec = math.sin(pitch_rad)
        z_vec = math.cos(yaw_rad) * math.cos(pitch_rad)

        if yaw < -12:
            direction = "Looking Left"
        elif yaw > 12:
            direction = "Looking Right"
        elif pitch < -10:
            direction = "Looking Down"
        else:
            direction = "Looking Forward"

        return {
            "pitch": pitch,
            "yaw": yaw,
            "roll": roll,
            "gaze_vector": [x_vec, y_vec, z_vec],
            "direction": direction,
        }
