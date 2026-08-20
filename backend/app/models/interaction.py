from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class ProductInteraction(Base):
    __tablename__ = "product_interactions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tracking_sessions.id", ondelete="CASCADE"), index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True)
    
    # Type of interaction: "viewed", "picked_up", "returned", "purchased", "compared"
    interaction_type = Column(String, index=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("TrackingSession")
    product = relationship("Product")
