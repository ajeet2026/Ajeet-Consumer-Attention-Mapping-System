from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.analytics_service import AnalyticsService
from app.dependencies.auth import get_current_user
from app.models.tracking import TrackingSession

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
