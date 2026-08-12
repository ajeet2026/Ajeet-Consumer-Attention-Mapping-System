from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database.database import Base


class DwellEvent(Base):
    __tablename__ = "dwell_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tracking_sessions.id"))
    shelf_id = Column(Integer, ForeignKey("shelves.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    duration = Column(Float, nullable=False)

    session = relationship("TrackingSession", back_populates="dwell_events")
    shelf = relationship("Shelf")
    product = relationship("Product")


class AnalyticsSummary(Base):
    __tablename__ = "analytics_summaries"

    id = Column(Integer, primary_key=True, index=True)
    average_attention_time = Column(Float, nullable=False)
    max_attention_time = Column(Float, nullable=False)
    repeated_attention_count = Column(Integer, nullable=False)
    top_shelf_id = Column(Integer, ForeignKey("shelves.id"), nullable=True)
    top_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    calculated_at = Column(DateTime, nullable=False)

    top_shelf = relationship("Shelf")
    top_product = relationship("Product")
