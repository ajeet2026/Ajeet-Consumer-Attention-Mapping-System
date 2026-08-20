import os

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

from app.ai.product_recognizer import ProductRecognizer

class ShelfProductDetector:
    """
    Detects individual products on retail shelves using YOLOv8
    fine-tuned on the SKU-110K dataset.

    SKU-110K is a single-class dataset ("object") that detects densely
    packed retail products on shelf images. Average shelf image contains
    ~150 products.

    The model weights are downloaded from Hugging Face:
    sbfisher/yolov8l-sku110k (trained at imgsz=640)
    """

    def __init__(self):
        self.model = None
        self.recognizer = ProductRecognizer()
        if HAS_YOLO:
            model_path = os.path.join(
                os.path.dirname(__file__), "yolov8_sku110k.pt"
            )
            if os.path.exists(model_path):
                try:
                    self.model = YOLO(model_path)
                    print(f"ShelfProductDetector: SKU-110K model loaded from {model_path}")
                except Exception as e:
                    print(f"ShelfProductDetector: Failed to load SKU-110K model: {e}")
            else:
                print(
                    f"ShelfProductDetector: Model not found at {model_path}. "
                    "Run scripts/download_sku110k_weights.py first."
                )

    def detect_products(self, frame, shelf_bbox=None, conf=0.25, max_det=500):
        """
        Detect individual products in a frame or shelf region.

        Args:
            frame: Full camera frame (BGR numpy array)
            shelf_bbox: Optional [x1, y1, x2, y2] to crop a specific shelf region.
                        If None, runs detection on the entire frame.
            conf: Confidence threshold (default 0.25)
            max_det: Maximum detections per image (default 500 for dense shelves)

        Returns:
            List of dicts: [{"bbox": [x1,y1,x2,y2], "confidence": float}]
            Coordinates are in the original frame's coordinate system.
        """
        if not self.model or frame is None or not HAS_CV2:
            return []

        # Crop to shelf region if provided
        offset_x, offset_y = 0, 0
        input_frame = frame
        if shelf_bbox:
            h, w = frame.shape[:2]
            x1, y1, x2, y2 = shelf_bbox
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 > x1 and y2 > y1:
                input_frame = frame[y1:y2, x1:x2]
                offset_x, offset_y = x1, y1
            else:
                return []

        try:
            results = self.model(
                input_frame,
                verbose=False,
                conf=conf,
                max_det=max_det,
            )

            detections = []
            for r in results:
                for box in r.boxes:
                    bx1, by1, bx2, by2 = box.xyxy[0].tolist()
                    c = float(box.conf[0])
                    detections.append({
                        "bbox": [
                            int(bx1 + offset_x),
                            int(by1 + offset_y),
                            int(bx2 + offset_x),
                            int(by2 + offset_y),
                        ],
                        "confidence": round(c, 3),
                    })

            return detections

        except Exception as e:
            print(f"ShelfProductDetector: Detection error: {e}")
            return []

    def count_products(self, frame, shelf_bbox=None, conf=0.25):
        """
        Count total products detected in a frame or shelf region.

        Returns:
            int: Number of products detected
        """
        return len(self.detect_products(frame, shelf_bbox, conf))

    def get_shelf_metrics(self, frame, shelf_bbox=None, conf=0.25):
        """
        Get comprehensive shelf metrics including product count,
        density score, and occupancy percentage.

        Args:
            frame: Full camera frame (BGR numpy array)
            shelf_bbox: Optional [x1,y1,x2,y2] shelf region

        Returns:
            dict with keys:
                product_count: int
                density_score: float (products per 10000 px²)
                occupancy_pct: float (% of shelf area covered by products)
                detections: list of detection dicts
        """
        detections = self.detect_products(frame, shelf_bbox, conf)
        product_count = len(detections)
        
        product_breakdown = {}

        # Calculate shelf area
        if shelf_bbox:
            x1, y1, x2, y2 = shelf_bbox
            shelf_area = max(1, (x2 - x1) * (y2 - y1))
        elif frame is not None:
            h, w = frame.shape[:2]
            shelf_area = w * h
        else:
            shelf_area = 1

        # Calculate total product bounding box area and run recognition
        product_area = 0
        for det in detections:
            bx1, by1, bx2, by2 = det["bbox"]
            product_area += (bx2 - bx1) * (by2 - by1)
            
            # Extract specific product identity
            try:
                # Ensure box is within frame boundaries
                h, w = frame.shape[:2]
                cx1, cy1 = max(0, bx1), max(0, by1)
                cx2, cy2 = min(w, bx2), min(h, by2)
                if cx2 > cx1 and cy2 > cy1:
                    crop = frame[cy1:cy2, cx1:cx2]
                    sku_name = self.recognizer.recognize_crop(crop)
                    det["product_name"] = sku_name
                    
                    if sku_name in product_breakdown:
                        product_breakdown[sku_name] += 1
                    else:
                        product_breakdown[sku_name] = 1
            except Exception as e:
                print(f"Failed to recognize crop: {e}")

        # Density: products per 10,000 square pixels
        density_score = round((product_count / shelf_area) * 10000, 2)

        # Occupancy: percentage of shelf covered by products
        occupancy_pct = round(min(100.0, (product_area / shelf_area) * 100), 1)

        return {
            "product_count": product_count,
            "density_score": density_score,
            "occupancy_pct": occupancy_pct,
            "detections": detections,
            "product_breakdown": product_breakdown,
        }

    def annotate_frame(self, frame, shelf_bbox=None, conf=0.25):
        """
        Draw product bounding boxes on the frame and return the annotated image.

        Returns:
            annotated_frame: numpy array with bounding boxes drawn
            metrics: dict from get_shelf_metrics
        """
        if frame is None or not HAS_CV2:
            return frame, {"product_count": 0, "density_score": 0, "occupancy_pct": 0, "detections": []}

        metrics = self.get_shelf_metrics(frame, shelf_bbox, conf)
        annotated = frame.copy()

        # Draw shelf region outline
        if shelf_bbox:
            x1, y1, x2, y2 = shelf_bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(
                annotated, f"Shelf Region",
                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 255), 1
            )

        # Draw product boxes
        for det in metrics["detections"]:
            bx1, by1, bx2, by2 = det["bbox"]
            cv2.rectangle(annotated, (bx1, by1), (bx2, by2), (0, 255, 0), 1)

        # Draw metrics overlay
        y_offset = 30
        if shelf_bbox:
            y_offset = shelf_bbox[1] + 20
        cv2.putText(
            annotated,
            f"Products: {metrics['product_count']} | Density: {metrics['density_score']} | Occupancy: {metrics['occupancy_pct']}%",
            (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (0, 255, 0), 2
        )

        return annotated, metrics
