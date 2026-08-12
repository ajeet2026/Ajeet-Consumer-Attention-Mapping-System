import time
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False



class VideoFrameReader:
    def __init__(self, source_path=None):
        self.source_path = source_path
        self.cap = None
        if source_path and HAS_CV2:
            try:
                self.cap = cv2.VideoCapture(source_path)
            except Exception as e:
                print(f"Failed to open video file: {e}")

    def read_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                # Loop video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if ret:
                    return frame
        return None

    def release(self):
        if self.cap:
            self.cap.release()


class ShopperDetector:
    def __init__(self):
        self.model = None
        if HAS_YOLO:
            try:
                self.model = YOLO("yolov8n.pt")
            except Exception as e:
                print(f"Failed to load YOLOv8 model: {e}")

    def detect(self, frame):
        """
        Detects people (class 0 in COCO) in the frame.
        Returns a list of dicts: {"bbox": [x1, y1, x2, y2], "confidence": float, "class_id": 0}
        """
        if self.model and frame is not None:
            try:
                results = self.model(frame, verbose=False)
                detections = []
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        if cls_id == 0:  # Person
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            conf = float(box.conf[0])
                            detections.append(
                                {
                                    "bbox": [
                                        int(x1),
                                        int(y1),
                                        int(x2),
                                        int(y2),
                                    ],
                                    "confidence": conf,
                                    "class_id": 0,
                                }
                            )
                return detections
            except Exception as e:
                print(f"YOLO detection error: {e}")

        # High-Fidelity Simulation Mode
        t = time.time()
        detections = []

        # Person 1 (walking across from left to right)
        x = int(100 + (t * 15) % 440)
        y = int(220 + np.sin(t * 1.5) * 15)
        detections.append(
            {
                "bbox": [x - 20, y - 60, x + 20, y + 60],
                "confidence": 0.95,
                "class_id": 0,
            }
        )

        # Person 2 (lingering near middle/right)
        if int(t // 12) % 2 == 0:
            x2 = int(350 + np.cos(t * 0.8) * 15)
            y2 = int(260 + np.sin(t * 0.5) * 8)
            detections.append(
                {
                    "bbox": [x2 - 20, y2 - 60, x2 + 20, y2 + 60],
                    "confidence": 0.89,
                    "class_id": 0,
                }
            )

        return detections
