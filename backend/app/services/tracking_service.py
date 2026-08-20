from datetime import datetime
from sqlalchemy.orm import Session
from app.models.tracking import TrackingSession, TrackingPoint, ZoneEvent


class TrackingService:
    @staticmethod
    def start_session(db: Session, camera_id: int, tracking_id: int, entry_time: datetime) -> TrackingSession:
        # Check if an open session already exists for this tracking ID and camera
        session = (
            db.query(TrackingSession)
            .filter(
                TrackingSession.camera_id == camera_id,
                TrackingSession.tracking_id == tracking_id,
                TrackingSession.exit_time == None,
            )
            .first()
        )

        if not session:
            session = TrackingSession(
                camera_id=camera_id,
                tracking_id=tracking_id,
                entry_time=entry_time,
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def end_session(db: Session, session_id: int, exit_time: datetime) -> TrackingSession:
        session = db.query(TrackingSession).filter(TrackingSession.id == session_id).first()
        if session and not session.exit_time:
            session.exit_time = exit_time
            session.duration = float((exit_time - session.entry_time).total_seconds())

            # Also close open zone events
            open_zones = (
                db.query(ZoneEvent)
                .filter(ZoneEvent.session_id == session_id, ZoneEvent.exit_time == None)
                .all()
            )
            for z in open_zones:
                z.exit_time = exit_time
                z.duration = float((exit_time - z.entry_time).total_seconds())

            db.commit()
            db.refresh(session)
            
            # Milestone 3 Integration: Trigger Behavior Engine on session end
            try:
                from app.services.behavior_service import BehaviorService
                BehaviorService.analyze_completed_session(db, session.id)
                print(f"✅ Behavior profile created for session {session_id}")
            except Exception as e:
                import traceback
                print(f"❌ Failed to analyze behavior for session {session_id}: {e}")
                traceback.print_exc()

        return session

    @staticmethod
    def add_point(db: Session, session_id: int, x: float, y: float, timestamp: datetime) -> TrackingPoint:
        point = TrackingPoint(
            session_id=session_id,
            timestamp=timestamp,
            x_coordinate=x,
            y_coordinate=y,
        )
        db.add(point)
        db.commit()
        return point

    @staticmethod
    def update_zone(db: Session, session_id: int, x: float, y: float, timestamp: datetime) -> ZoneEvent:
        """
        Determines the shopper's zone and manages ZoneEvent lifecycles.
        Simplified 2D polygons based on coordinate boundaries:
        - Entrance: X < 180
        - Shelf A (Beverages): 180 <= X <= 340, Y < 240
        - Shelf B (Snacks): X > 340, Y < 240
        - Checkout: Y >= 240
        """
        # Determine Zone
        if y >= 240:
            current_zone = "Checkout"
        elif x < 180:
            current_zone = "Entrance"
        elif x <= 340:
            current_zone = "Shelf A"
        else:
            current_zone = "Shelf B"

        # Check if the active zone event is already for the current zone
        active_zone_event = (
            db.query(ZoneEvent)
            .filter(ZoneEvent.session_id == session_id, ZoneEvent.exit_time == None)
            .first()
        )

        if active_zone_event:
            if active_zone_event.zone_id == current_zone:
                # Still in the same zone, do nothing
                return active_zone_event
            else:
                # Left the previous zone, close it
                active_zone_event.exit_time = timestamp
                active_zone_event.duration = float(
                    (timestamp - active_zone_event.entry_time).total_seconds()
                )

        # Enter the new zone
        new_zone_event = ZoneEvent(
            session_id=session_id,
            zone_id=current_zone,
            entry_time=timestamp,
        )
        db.add(new_zone_event)
        db.commit()
        db.refresh(new_zone_event)
        return new_zone_event
