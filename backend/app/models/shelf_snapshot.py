from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.database import Base


class ShelfSnapshot(Base):
    __tablename__ = "shelf_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    shelf_id = Column(Integer, ForeignKey("shelves.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    product_count = Column(Integer, default=0)
    density_score = Column(Float, default=0.0)
    occupancy_pct = Column(Float, default=0.0)
    snapshot_path = Column(String, nullable=True)  # Path to annotated image
    product_breakdown = Column(JSON, nullable=True)  # JSON object storing product counts

    shelf = relationship("Shelf", back_populates="snapshots")
