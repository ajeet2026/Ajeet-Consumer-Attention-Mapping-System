from sqlalchemy.orm import Session
from app.models.attention import AttentionEvent
from app.models.shelf import Shelf

class PreferenceService:
    """
    Phase 4: Product preference analysis
    Use product-view, attention, and interaction data to determine preferences.
    """
    
    @staticmethod
    def analyze_preferences(db: Session, session_id: int):
        # Fetch all attention events for the session
        attention_events = db.query(AttentionEvent).filter(AttentionEvent.session_id == session_id).all()
        
        if not attention_events:
            return {
                "preferred_category": None,
                "top_viewed_shelf_id": None
            }
            
        # Count attention by shelf
        shelf_counts = {}
        for ae in attention_events:
            shelf_counts[ae.shelf_id] = shelf_counts.get(ae.shelf_id, 0) + 1
            
        # Find the most viewed shelf
        top_shelf_id = max(shelf_counts, key=shelf_counts.get)
        
        # Get category of that shelf
        top_shelf = db.query(Shelf).filter(Shelf.id == top_shelf_id).first()
        preferred_category = "Unknown Category"
        if top_shelf:
            # For this project, shelf name often acts as category (e.g. "Beverages", "Snacks")
            preferred_category = top_shelf.name
            
        return {
            "preferred_category": preferred_category,
            "top_viewed_shelf_id": top_shelf_id
        }
