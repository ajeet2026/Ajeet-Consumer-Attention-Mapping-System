from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database.database import Base


class AttentionEvent(Base):
    __tablename__ = "attention_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tracking_sessions.id"))
    shelf_id = Column(Integer, ForeignKey("shelves.id"), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)

    session = relationship("TrackingSession", back_populates="attention_events")
    shelf = relationship("Shelf")
