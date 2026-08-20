from sqlalchemy.orm import Session
from app.models.tracking import TrackingSession, TrackingPoint, ZoneEvent
from app.models.attention import AttentionEvent
from app.models.shelf import Shelf

class BehaviorFeaturesService:
    """
    Phase 2: Build a behavior feature layer.
    Converts raw events into measurable behavioral features.
    """
    
    @staticmethod
    def calculate_features(db: Session, session: TrackingSession):
        # Time calculations
        visit_duration = 0.0
        if session.exit_time:
            visit_duration = (session.exit_time - session.entry_time).total_seconds()
        
        # Zones visited
        zone_events = db.query(ZoneEvent).filter(ZoneEvent.session_id == session.id).order_by(ZoneEvent.entry_time).all()
        unique_zones = len(set([ze.zone_id for ze in zone_events]))
        
        # Repeat zone visits
        repeat_zone_visits = 0
        if len(zone_events) > unique_zones:
            repeat_zone_visits = len(zone_events) - unique_zones
            
        # Attention and products
        attention_events = db.query(AttentionEvent).filter(AttentionEvent.session_id == session.id).all()
        
        # Calculate approximate attention time
        # Each attention event represents about 1 second of gaze
        total_attention_seconds = len(attention_events) * 1.0
        
        # Unique products/shelves viewed
        shelves_viewed = set([ae.shelf_id for ae in attention_events if ae.shelf_id is not None])
        products_viewed = len(shelves_viewed) * 5  # Placeholder: assume 5 products viewed per shelf gaze
        
        # Simulate picks and returns for now (until physical interaction model is implemented)
        # We can guess based on high attention duration on a single shelf
        products_picked = 0
        comparisons = 0
        
        # Count attention events per shelf to estimate interaction
        shelf_attention_counts = {}
        for ae in attention_events:
            if ae.shelf_id is not None:
                shelf_attention_counts[ae.shelf_id] = shelf_attention_counts.get(ae.shelf_id, 0) + 1
            
        for shelf_id, count in shelf_attention_counts.items():
            if count > 10:  # If looked at shelf for > 10 frames
                products_picked += 1
                
        # If looked at multiple shelves multiple times, it's a comparison
        if len(shelves_viewed) > 1 and repeat_zone_visits > 0:
            comparisons = len(shelves_viewed) - 1
            
        # Movement distance
        points = db.query(TrackingPoint).filter(TrackingPoint.session_id == session.id).order_by(TrackingPoint.timestamp).all()
        movement_distance = 0.0
        for i in range(1, len(points)):
            p1 = points[i-1]
            p2 = points[i]
            # Simple Euclidean distance
            dist = ((p2.x_coordinate - p1.x_coordinate)**2 + (p2.y_coordinate - p1.y_coordinate)**2)**0.5
            movement_distance += dist
            
        return {
            "visit_duration": round(visit_duration, 2),
            "zones_visited": unique_zones,
            "repeat_zone_visits": repeat_zone_visits,
            "total_attention_seconds": total_attention_seconds,
            "products_viewed": products_viewed,
            "products_picked": products_picked,
            "comparisons": comparisons,
            "movement_distance": round(movement_distance, 2)
        }
