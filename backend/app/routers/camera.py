import time
import io
import os
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.camera import Camera
from app.schemas.camera_schema import (
    CameraCreate,
    CameraUpdate,
    CameraResponse,
)
from app.dependencies.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/cameras", tags=["Cameras"])


# Check dependencies for mock video streaming
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    try:
        from PIL import Image, ImageDraw
        HAS_PIL = True
    except ImportError:
        HAS_PIL = False


def generate_frames_cv2(camera_id: int, camera_name: str, video_path: str = None):
    from app.database.database import SessionLocal
    from app.ai.detector import VideoFrameReader, ShopperDetector
    from app.ai.tracker import ShopperTracker
    from app.ai.gaze import GazeEstimator
    from app.ai.attention import AttentionDetector
    from app.services.tracking_service import TrackingService
    from app.services.attention_service import AttentionService
    from app.models.shelf import Shelf

    reader = VideoFrameReader(video_path)
    detector = ShopperDetector()
    tracker = ShopperTracker()
    gaze_estimator = GazeEstimator()
    attention_detector = AttentionDetector()

    db = SessionLocal()
    shelves = db.query(Shelf).all()
    active_sessions = {}

    width, height = 640, 480
    frame_count = 0
    start_time = time.time()
    fps = 10.0

    try:
        while True:
            frame = None
            if video_path and os.path.exists(video_path):
                frame = reader.read_frame()
                if frame is not None:
                    frame = cv2.resize(frame, (width, height))

            if frame is None:
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[:] = (42, 23, 15)  # Dark slate background BGR: 15, 23, 42
                # Draw mock layout
                cv2.rectangle(frame, (40, 60), (240, 280), (30, 40, 50), 2)
                cv2.putText(
                    frame,
                    "SHELF A",
                    (80, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (148, 163, 184),
                    1,
                )
                cv2.rectangle(frame, (380, 60), (580, 280), (30, 40, 50), 2)
                cv2.putText(
                    frame,
                    "SHELF B",
                    (420, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (148, 163, 184),
                    1,
                )

            detections = detector.detect(frame)
            bboxes = [d["bbox"] for d in detections]
            tracked_objects = tracker.update(bboxes)
            now = datetime.utcnow()

            # End missing sessions
            current_ids = set(tracked_objects.keys())
            for trk_id in list(active_sessions.keys()):
                if trk_id not in current_ids:
                    TrackingService.end_session(db, active_sessions[trk_id], now)
                    del active_sessions[trk_id]

            # Process active tracks
            for trk_id, bbox in tracked_objects.items():
                cx = int((bbox[0] + bbox[2]) / 2)
                cy = int((bbox[1] + bbox[3]) / 2)

                if trk_id not in active_sessions:
                    sess = TrackingService.start_session(
                        db, camera_id, trk_id, now
                    )
                    active_sessions[trk_id] = sess.id

                sess_id = active_sessions[trk_id]
                TrackingService.add_point(
                    db, sess_id, float(cx), float(cy), now
                )
                TrackingService.update_zone(
                    db, sess_id, float(cx), float(cy), now
                )

                gaze_data = gaze_estimator.estimate_gaze(frame, bbox)
                gaze_vector = gaze_data["gaze_vector"]

                looked_shelf_id = attention_detector.detect_attention(
                    (cx, cy), gaze_vector, shelves
                )
                AttentionService.update_attention(
                    db, sess_id, looked_shelf_id, now
                )

                # Draw Person bounding box
                cv2.rectangle(
                    frame,
                    (bbox[0], bbox[1]),
                    (bbox[2], bbox[3]),
                    (34, 197, 94),
                    2,
                )
                cv2.putText(
                    frame,
                    f"Shopper #{trk_id}",
                    (bbox[0], bbox[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (34, 197, 94),
                    2,
                )

                # Draw Gaze Arrow
                vx_pixel = int(gaze_vector[0] * 80)
                vy_pixel = int(gaze_vector[1] * 80)
                cv2.arrowedLine(
                    frame,
                    (cx, cy),
                    (cx + vx_pixel, cy + vy_pixel),
                    (37, 99, 235),
                    2,
                    tipLength=0.3,
                )

                if looked_shelf_id:
                    shelf_name = next(
                        (s.name for s in shelves if s.id == looked_shelf_id),
                        f"Shelf {looked_shelf_id}",
                    )
                    cv2.putText(
                        frame,
                        f"Focus: {shelf_name}",
                        (bbox[0], bbox[3] + 18),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (235, 99, 37),
                        1,
                    )

            # Draw standard overlays
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed > 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                start_time = time.time()

            cv2.putText(
                frame,
                f"Time: {time.strftime('%H:%M:%S')}",
                (470, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (148, 163, 184),
                1,
            )
            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (148, 163, 184),
                1,
            )
            cv2.putText(
                frame,
                f"Camera: {camera_name}",
                (20, 455),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (148, 163, 184),
                1,
            )

            ret, jpeg = cv2.imencode(".jpg", frame)
            if not ret:
                continue
            frame_bytes = jpeg.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            time.sleep(0.08)
    finally:
        reader.release()
        db.close()


def generate_frames_pil(camera_id: int, camera_name: str, video_path: str = None):
    from app.database.database import SessionLocal
    from app.ai.detector import ShopperDetector
    from app.ai.tracker import ShopperTracker
    from app.ai.gaze import GazeEstimator
    from app.ai.attention import AttentionDetector
    from app.services.tracking_service import TrackingService
    from app.services.attention_service import AttentionService
    from app.models.shelf import Shelf

    db = SessionLocal()
    detector = ShopperDetector()
    tracker = ShopperTracker()
    gaze_estimator = GazeEstimator()
    attention_detector = AttentionDetector()
    shelves = db.query(Shelf).all()
    active_sessions = {}

    width, height = 640, 480
    frame_count = 0
    start_time = time.time()
    fps = 10.0

    try:
        while True:
            img = Image.new("RGB", (width, height), (15, 23, 42))
            draw = ImageDraw.Draw(img)

            # Draw Mock Layout
            draw.rectangle([40, 60, 240, 280], outline=(30, 40, 50), width=2)
            draw.text((80, 40), "SHELF A", fill=(148, 163, 184))
            draw.rectangle([380, 60, 580, 280], outline=(30, 40, 50), width=2)
            draw.text((420, 40), "SHELF B", fill=(148, 163, 184))

            detections = detector.detect(None)
            bboxes = [d["bbox"] for d in detections]
            tracked_objects = tracker.update(bboxes)
            now = datetime.utcnow()

            # End missing sessions
            current_ids = set(tracked_objects.keys())
            for trk_id in list(active_sessions.keys()):
                if trk_id not in current_ids:
                    TrackingService.end_session(db, active_sessions[trk_id], now)
                    del active_sessions[trk_id]

            # Process active tracks
            for trk_id, bbox in tracked_objects.items():
                cx = int((bbox[0] + bbox[2]) / 2)
                cy = int((bbox[1] + bbox[3]) / 2)

                if trk_id not in active_sessions:
                    sess = TrackingService.start_session(
                        db, camera_id, trk_id, now
                    )
                    active_sessions[trk_id] = sess.id

                sess_id = active_sessions[trk_id]
                TrackingService.add_point(
                    db, sess_id, float(cx), float(cy), now
                )
                TrackingService.update_zone(
                    db, sess_id, float(cx), float(cy), now
                )

                gaze_data = gaze_estimator.estimate_gaze(None, bbox)
                gaze_vector = gaze_data["gaze_vector"]

                looked_shelf_id = attention_detector.detect_attention(
                    (cx, cy), gaze_vector, shelves
                )
                AttentionService.update_attention(
                    db, sess_id, looked_shelf_id, now
                )

                # Draw Person Bounding Box
                draw.rectangle(
                    [bbox[0], bbox[1], bbox[2], bbox[3]],
                    outline=(34, 197, 94),
                    width=2,
                )
                draw.text(
                    (bbox[0], bbox[1] - 15),
                    f"Shopper #{trk_id}",
                    fill=(34, 197, 94),
                )

                # Draw Gaze Arrow line
                vx = int(gaze_vector[0] * 80)
                vy = int(gaze_vector[1] * 80)
                draw.line(
                    [cx, cy, cx + vx, cy + vy], fill=(37, 99, 235), width=2
                )

                if looked_shelf_id:
                    shelf_name = next(
                        (s.name for s in shelves if s.id == looked_shelf_id),
                        f"Shelf {looked_shelf_id}",
                    )
                    draw.text(
                        (bbox[0], bbox[3] + 5),
                        f"Focus: {shelf_name}",
                        fill=(235, 99, 37),
                    )

            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed > 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                start_time = time.time()

            draw.text((20, 20), f"FPS: {fps:.1f}", fill=(148, 163, 184))
            draw.text(
                (470, 20),
                f"Time: {time.strftime('%H:%M:%S')}",
                fill=(148, 163, 184),
            )
            draw.text((20, 450), f"Camera: {camera_name}", fill=(148, 163, 184))

            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            frame_bytes = buf.getvalue()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            time.sleep(0.1)
    finally:
        db.close()



@router.post("/", response_model=CameraResponse)
def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    new_camera = Camera(
        name=camera.name,
        ip_address=camera.ip_address,
        store_id=camera.store_id,
    )
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera


@router.get("/", response_model=list[CameraResponse])
def get_cameras(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Camera).all()


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    data: CameraUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    camera.name = data.name
    camera.ip_address = data.ip_address
    camera.store_id = data.store_id
    db.commit()
    db.refresh(camera)
    return camera


@router.delete("/{camera_id}")
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Cascade-delete related tracking data to avoid FK constraint errors
    try:
        from app.models.tracking import TrackingSession, TrackingPoint, ZoneEvent
        from app.models.attention import AttentionEvent
        from app.models.dwell import DwellEvent

        sessions = db.query(TrackingSession).filter(
            TrackingSession.camera_id == camera_id
        ).all()
        session_ids = [s.id for s in sessions]

        if session_ids:
            db.query(DwellEvent).filter(DwellEvent.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(AttentionEvent).filter(AttentionEvent.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(ZoneEvent).filter(ZoneEvent.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(TrackingPoint).filter(TrackingPoint.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(TrackingSession).filter(TrackingSession.camera_id == camera_id).delete(synchronize_session=False)
    except Exception:
        pass  # Tables may not exist yet

    # Delete uploaded video file if it exists
    if camera.ip_address and os.path.isfile(camera.ip_address):
        try:
            os.remove(camera.ip_address)
        except OSError:
            pass

    db.delete(camera)
    db.commit()
    return {"message": "Camera deleted successfully"}


@router.get("/{camera_id}/feed")
def get_camera_feed(
    camera_id: int,
    request: Request,
    token: str = None,
    db: Session = Depends(get_db),
):
    actual_token = token
    if not actual_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            actual_token = auth_header.split(" ")[1]

    if not actual_token:
        raise HTTPException(status_code=401, detail="Not authorized")

    from app.utils.security import decode_access_token
    payload = decode_access_token(actual_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Generate stream
    if HAS_CV2:
        frame_generator = generate_frames_cv2(camera.id, camera.name, camera.ip_address)
    elif HAS_PIL:
        frame_generator = generate_frames_pil(camera.id, camera.name, camera.ip_address)
    else:
        # Extreme fallback: blank jpeg bytes generator
        def blank_generator():
            # A tiny 1x1 black pixel JPEG
            blank_jpeg = (
                b"\xff\xd8\xff\xdb\x00\x43\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07"
                b"\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f"
                b"\x1e\x1d\x1a\x1c\x1c\x20\x24\x2e\x27\x20\x22\x2c\x23\x1c\x1c\x28\x37"
                b"\x29\x2c\x30\x31\x34\x34\x34\x1f\x27\x39\x3d\x38\x32\x3c\x2e\x33\x34"
                b"\x32\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00"
                b"\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00"
                b"\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01"
                b"\x01\x00\x00\x3f\x00\x37\xff\xd9"
            )
            while True:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + blank_jpeg
                    + b"\r\n"
                )
                time.sleep(1.0)

        frame_generator = blank_generator()

    return StreamingResponse(
        frame_generator,
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/upload", response_model=CameraResponse)
def upload_camera_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".mp4", ".avi", ".mov", ".mkv"]:
        raise HTTPException(
            status_code=400, detail="Only video files (.mp4, .avi, .mov, .mkv) are allowed"
        )

    # ensure uploads directory exists
    uploads_dir = "/Users/ajeetkumar/Desktop/project/ConsumerAttentionMapping/backend/uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    # Save the file locally
    file_path = os.path.join(uploads_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save video: {str(e)}"
        )

    # Register as a Virtual Camera (defaulting to store 1)
    new_camera = Camera(
        name=f"Video: {file.filename}",
        ip_address=file_path,
        store_id=1,
    )
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera

