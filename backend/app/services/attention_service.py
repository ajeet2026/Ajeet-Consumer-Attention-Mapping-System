from datetime import datetime
from sqlalchemy.orm import Session
from app.models.attention import AttentionEvent
from app.models.dwell import DwellEvent


class AttentionService:
    @staticmethod
    def update_attention(
        db: Session, session_id: int, shelf_id: int, timestamp: datetime
    ) -> AttentionEvent:
        """
        Manages the lifecycle of AttentionEvents and DwellEvents.
        """
        active_event = (
            db.query(AttentionEvent)
            .filter(
                AttentionEvent.session_id == session_id,
                AttentionEvent.end_time == None,
            )
            .first()
        )

        if active_event:
            if active_event.shelf_id == shelf_id:
                # Still focused on the same shelf
                return active_event
            else:
                # Focus shifted, close active event
                active_event.end_time = timestamp
                duration = float(
                    (timestamp - active_event.start_time).total_seconds()
                )
                active_event.duration = duration

                # Create a corresponding DwellEvent for metrics
                if active_event.shelf_id:
                    dwell = DwellEvent(
                        session_id=session_id,
                        shelf_id=active_event.shelf_id,
                        duration=duration,
                    )
                    db.add(dwell)

                db.commit()

        # Open new attention event if looking at a shelf
        if shelf_id is not None:
            new_event = AttentionEvent(
                session_id=session_id,
                shelf_id=shelf_id,
                start_time=timestamp,
            )
            db.add(new_event)
            db.commit()
            db.refresh(new_event)
            return new_event

        return None
