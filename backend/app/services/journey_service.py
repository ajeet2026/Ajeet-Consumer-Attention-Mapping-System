from sqlalchemy.orm import Session
from app.models.tracking import ZoneEvent

class JourneyService:
    """
    Phase 5 & 6: Movement behavior and Journey analytics
    Create a complete shopper-journey summary from movement and session data.
    """
    
    @staticmethod
    def analyze_journey(db: Session, session_id: int):
        zone_events = db.query(ZoneEvent).filter(ZoneEvent.session_id == session_id).order_by(ZoneEvent.entry_time).all()
        
        if not zone_events:
            return {
                "journey_path": ["Entrance", "Checkout"],
                "longest_dwell_zone": None,
                "first_zone": None,
                "last_zone": None
            }
            
        path = []
        current_zone = None
        
        for ze in zone_events:
            # Simple de-jitter: Ignore zone events that lasted less than 1 second, 
            # unless it's the very first or last event
            if ze.duration is not None and ze.duration < 1.0:
                continue
                
            if ze.zone_id != current_zone:
                path.append(ze.zone_id)
                current_zone = ze.zone_id
                
        # Fallbacks in case tracking missed the entry/exit points
        if not path or path[0] != "Entrance":
            path.insert(0, "Entrance")
        if path[-1] != "Checkout":
            path.append("Checkout")
        
        # Calculate approximate dwell per zone
        zone_counts = {}
        for ze in zone_events:
            zone_counts[ze.zone_id] = zone_counts.get(ze.zone_id, 0) + 1
            
        longest_dwell_zone = None
        if zone_counts:
            longest_dwell_zone = max(zone_counts, key=zone_counts.get)
            
        return {
            "journey_path": path,
            "longest_dwell_zone": longest_dwell_zone,
            "first_zone": path[1] if len(path) > 2 else None,
            "last_zone": path[-2] if len(path) > 2 else None
        }
