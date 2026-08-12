from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database.database import Base


class TrackingSession(Base):
    __tablename__ = "tracking_sessions"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, index=True)  # ID from ByteTrack
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # in seconds

    camera = relationship("Camera")
    points = relationship(
        "TrackingPoint", back_populates="session", cascade="all, delete"
    )
    zone_events = relationship(
        "ZoneEvent", back_populates="session", cascade="all, delete"
    )
    attention_events = relationship(
        "AttentionEvent", back_populates="session", cascade="all, delete"
    )
    dwell_events = relationship(
        "DwellEvent", back_populates="session", cascade="all, delete"
    )


class TrackingPoint(Base):
    __tablename__ = "tracking_points"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tracking_sessions.id"))
    timestamp = Column(DateTime, nullable=False)
    x_coordinate = Column(Float, nullable=False)
    y_coordinate = Column(Float, nullable=False)

    session = relationship("TrackingSession", back_populates="points")


class ZoneEvent(Base):
    __tablename__ = "zone_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tracking_sessions.id"))
    zone_id = Column(
        String, nullable=False
    )  # e.g., "Entrance", "Shelf A", "Checkout"
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)

    session = relationship("TrackingSession", back_populates="zone_events")
