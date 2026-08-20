from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.tracking import TrackingSession, TrackingPoint, ZoneEvent
from app.models.attention import AttentionEvent
from app.models.dwell import DwellEvent


class AnalyticsService:
    @staticmethod
    def get_live_stats(db: Session):
        """
        Returns live metric aggregates.
        """
        active_shoppers = (
            db.query(TrackingSession)
            .filter(TrackingSession.exit_time == None)
            .count()
        )

        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_visitors = (
            db.query(TrackingSession)
            .filter(TrackingSession.entry_time >= today_start)
            .count()
        )

        avg_dwell = (
            db.query(func.avg(TrackingSession.duration))
            .filter(
                TrackingSession.entry_time >= today_start,
                TrackingSession.exit_time != None,
            )
            .scalar()
            or 0.0
        )

        attention_count = (
            db.query(AttentionEvent)
            .filter(AttentionEvent.start_time >= today_start)
            .count()
        )

        # Get top performing shelf
        top_shelf_query = (
            db.query(
                DwellEvent.shelf_id,
                func.sum(DwellEvent.duration).label("total_duration"),
            )
            .group_by(DwellEvent.shelf_id)
            .order_by(func.sum(DwellEvent.duration).desc())
            .first()
        )

        top_shelf_id = top_shelf_query[0] if top_shelf_query else None

        return {
            "active_shoppers": active_shoppers,
            "today_visitors": today_visitors,
            "average_dwell_time": round(float(avg_dwell), 1),
            "attention_events_count": attention_count,
            "top_shelf_id": top_shelf_id,
        }

    @staticmethod
    def get_heatmap_points(db: Session, limit: int = 1200):
        """
        Returns coordinate history for heatmap drawing.
        """
        points = (
            db.query(TrackingPoint)
            .order_by(TrackingPoint.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {"x": p.x_coordinate, "y": p.y_coordinate, "value": 1.0}
            for p in points
        ]

    @staticmethod
    def get_dwell_stats(db: Session):
        """
        Returns total dwell time and views grouped by shelf.
        """
        results = (
            db.query(
                DwellEvent.shelf_id,
                func.sum(DwellEvent.duration).label("total_duration"),
                func.count(DwellEvent.id).label("visit_count"),
            )
            .group_by(DwellEvent.shelf_id)
            .all()
        )

        stats = []
        for r in results:
            if r.shelf_id:
                stats.append(
                    {
                        "shelf_id": r.shelf_id,
                        "total_dwell_time": float(r.total_duration),
                        "view_count": r.visit_count,
                    }
                )
        return stats

    @staticmethod
    def get_zone_analytics(db: Session):
        """
        Returns shopper visit counts and duration per zone.
        """
        results = (
            db.query(
                ZoneEvent.zone_id,
                func.count(ZoneEvent.id).label("visit_count"),
                func.avg(ZoneEvent.duration).label("avg_duration"),
            )
            .group_by(ZoneEvent.zone_id)
            .all()
        )

        return [
            {
                "zone_id": r.zone_id,
                "visit_count": r.visit_count,
                "average_duration": round(float(r.avg_duration or 0.0), 1),
            }
            for r in results
        ]

    @staticmethod
    def get_shopper_path(db: Session, session_id: int):
        """
        Returns the path points and zone events for a specific shopper session.
        """
        points = (
            db.query(TrackingPoint)
            .filter(TrackingPoint.session_id == session_id)
            .order_by(TrackingPoint.timestamp.asc())
            .all()
        )
        
        zones = (
            db.query(ZoneEvent)
            .filter(ZoneEvent.session_id == session_id)
            .order_by(ZoneEvent.entry_time.asc())
            .all()
        )

        path_data = [
            {"x": p.x_coordinate, "y": p.y_coordinate, "timestamp": p.timestamp}
            for p in points
        ]
        
        zone_data = [
            {
                "zone_id": z.zone_id,
                "entry_time": z.entry_time,
                "exit_time": z.exit_time,
                "duration": z.duration
            }
            for z in zones
        ]

        return {
            "session_id": session_id,
            "path": path_data,
            "zones": zone_data
        }

