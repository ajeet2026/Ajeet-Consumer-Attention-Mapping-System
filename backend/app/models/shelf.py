from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Shelf(Base):
    __tablename__ = "shelves"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    store_id = Column(
        Integer,
        ForeignKey("stores.id")
    )

    # Camera-view bounding box for this shelf (pixel coordinates)
    bbox_x1 = Column(Integer, nullable=True)
    bbox_y1 = Column(Integer, nullable=True)
    bbox_x2 = Column(Integer, nullable=True)
    bbox_y2 = Column(Integer, nullable=True)

    store = relationship(
        "Store",
        back_populates="shelves"
    )

    products = relationship(
        "Product",
        back_populates="shelf",
        cascade="all, delete"
    )

    snapshots = relationship(
        "ShelfSnapshot",
        back_populates="shelf",
        cascade="all, delete"
    )