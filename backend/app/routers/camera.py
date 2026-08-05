import time
import io
from fastapi import APIRouter, Depends, HTTPException, Request
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


def generate_frames_cv2(camera_name: str):
    width, height = 640, 480
    x, y = 100, 100
    dx, dy = 8, 6
    radius = 25
    color = (235, 99, 37)  # Orange

    while True:
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:] = (42, 23, 15)  # Dark background (BGR: 15, 23, 42)

        x += dx
        y += dy
        if x - radius < 0 or x + radius > width:
            dx = -dx
        if y - radius < 0 or y + radius > height:
            dy = -dy

        # Bouncing circle
        cv2.circle(img, (x, y), radius, color, -1)
        cv2.circle(img, (x, y), radius + 5, (255, 255, 255), 2)

        # Drawing text overlay
        cv2.putText(
            img,
            f"LIVE: {camera_name}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            img,
            f"Time: {time.strftime('%H:%M:%S')}",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (148, 163, 184),
            1,
        )
        cv2.putText(
            img,
            "Milestone 1 - Stream Active",
            (30, 430),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (34, 197, 94),
            1,
        )

        ret, jpeg = cv2.imencode(".jpg", img)
        if not ret:
            continue
        frame = jpeg.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )
        time.sleep(0.1)  # ~10 FPS


def generate_frames_pil(camera_name: str):
    width, height = 640, 480
    x, y = 100, 100
    dx, dy = 12, 10
    radius = 25

    while True:
        img = Image.new("RGB", (width, height), (15, 23, 42))
        draw = ImageDraw.Draw(img)

        x += dx
        y += dy
        if x - radius < 0 or x + radius > width:
            dx = -dx
        if y - radius < 0 or y + radius > height:
            dy = -dy

        # Bouncing circle
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=(37, 99, 235),
            outline=(255, 255, 255),
        )

        # Text overlay
        draw.text((30, 30), f"LIVE: {camera_name}", fill=(255, 255, 255))
        draw.text(
            (30, 60), f"Time: {time.strftime('%H:%M:%S')}", fill=(148, 163, 184)
        )
        draw.text(
            (30, 430), "Milestone 1 - Stream Active (Fallback)", fill=(34, 197, 94)
        )

        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        frame = buf.getvalue()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )
        time.sleep(0.1)


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
        frame_generator = generate_frames_cv2(camera.name)
    elif HAS_PIL:
        frame_generator = generate_frames_pil(camera.name)
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
