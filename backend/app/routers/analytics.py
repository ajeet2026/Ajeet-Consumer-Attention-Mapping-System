from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.shelf_analytics_service import ShelfAnalyticsService
from app.dependencies.auth import get_current_user
from app.models.tracking import TrackingSession
from app.models.shelf import Shelf

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/live")
def get_live_metrics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return AnalyticsService.get_live_stats(db)


@router.get("/shoppers")
def get_shopper_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch recent sessions
    sessions = (
        db.query(TrackingSession)
        .order_by(TrackingSession.entry_time.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": s.id,
            "tracking_id": s.tracking_id,
            "camera_id": s.camera_id,
            "entry_time": s.entry_time,
            "exit_time": s.exit_time,
            "duration": s.duration,
        }
        for s in sessions
    ]


@router.get("/dwell")
def get_dwell_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return AnalyticsService.get_dwell_stats(db)


@router.get("/attention")
def get_attention_heatmap(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return AnalyticsService.get_heatmap_points(db)


@router.get("/zones")
def get_zone_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return AnalyticsService.get_zone_analytics(db)


@router.get("/sessions/{session_id}/path")
def get_session_path(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return AnalyticsService.get_shopper_path(db, session_id)


# ---- Shelf Product Analytics (SKU-110K) ---- #


@router.get("/shelf/summary")
def get_all_shelves_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get latest product detection summary for all shelves."""
    return ShelfAnalyticsService.get_all_shelves_summary(db)


@router.get("/shelf/{shelf_id}/history")
def get_shelf_history(
    shelf_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get historical shelf snapshots (product counts over time)."""
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    return ShelfAnalyticsService.get_shelf_history(db, shelf_id)


@router.post("/shelf/{shelf_id}/scan")
def trigger_shelf_scan(
    shelf_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Trigger a live shelf product scan using the SKU-110K model.
    Reads the current camera frame, detects products, and saves a snapshot.
    """
    from app.ai.shelf_detector import ShelfProductDetector
    from app.ai.detector import VideoFrameReader
    from app.models.camera import Camera
    import cv2
    import os

    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")

    # Get the shelf's bounding box
    shelf_bbox = ShelfAnalyticsService.get_shelf_bbox(shelf)

    # Find a camera with a video file to read from
    camera = db.query(Camera).first()
    if not camera:
        raise HTTPException(status_code=404, detail="No camera configured")

    video_path = None
    if camera.ip_address and os.path.exists(camera.ip_address):
        video_path = camera.ip_address
    if not video_path and os.path.exists("uploads"):
        for f in os.listdir("uploads"):
            if f.endswith((".mp4", ".avi", ".mkv")):
                video_path = os.path.join("uploads", f)
                break

    if not video_path:
        raise HTTPException(status_code=404, detail="No video source found")

    # Read a frame from the video
    reader = VideoFrameReader(video_path)
    frame = reader.read_frame()
    reader.release()

    if frame is None:
        raise HTTPException(status_code=500, detail="Failed to read video frame")

    frame = cv2.resize(frame, (640, 480))

    # Run shelf product detection
    detector = ShelfProductDetector()
    if not detector.model:
        raise HTTPException(status_code=500, detail="SKU-110K model not loaded")

    metrics = detector.get_shelf_metrics(frame, shelf_bbox)

    # Save annotated image
    annotated, _ = detector.annotate_frame(frame, shelf_bbox)
    snapshot_dir = os.path.join("uploads", "shelf_snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)
    snapshot_filename = f"shelf_{shelf_id}_{int(__import__('time').time())}.jpg"
    snapshot_path = os.path.join(snapshot_dir, snapshot_filename)
    cv2.imwrite(snapshot_path, annotated)

    # Save to database
    snapshot = ShelfAnalyticsService.save_snapshot(
        db, shelf_id, metrics, snapshot_path
    )

    return {
        "shelf_id": shelf_id,
        "shelf_name": shelf.name,
        "product_count": metrics["product_count"],
        "density_score": metrics["density_score"],
        "occupancy_pct": metrics["occupancy_pct"],
        "snapshot_id": snapshot.id,
        "snapshot_path": snapshot_path,
        "product_breakdown": metrics.get("product_breakdown", {}),
        "detections": metrics["detections"][:20],  # Return first 20 for API response
        "total_detections": len(metrics["detections"]),
    }
