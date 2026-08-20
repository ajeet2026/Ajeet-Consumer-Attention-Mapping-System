from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tracking_sessions.id", ondelete="CASCADE"), index=True, unique=True)
    shopper_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Features
    visit_duration = Column(Float, default=0.0)
    zones_visited = Column(Integer, default=0)
    products_viewed = Column(Integer, default=0)
    products_picked = Column(Integer, default=0)
    comparisons = Column(Integer, default=0)
    total_attention_seconds = Column(Float, default=0.0)

    # Derived Profile
    preferred_category = Column(String, nullable=True)
    segment = Column(String, index=True)  # Explorer, Quick Buyer, etc.
    confidence = Column(Float, default=1.0)
    
    # Complex JSON Data
    journey_path = Column(JSON, default=list)

    # Relationships
    session = relationship("TrackingSession", backref="behavior_profile")
