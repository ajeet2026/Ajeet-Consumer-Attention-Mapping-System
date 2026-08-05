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

    store = relationship(
        "Store",
        back_populates="shelves"
    )

    products = relationship(
        "Product",
        back_populates="shelf",
        cascade="all, delete"
    )