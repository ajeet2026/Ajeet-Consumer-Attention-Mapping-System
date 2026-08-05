from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    brand = Column(String)

    price = Column(Integer)

    shelf_id = Column(
        Integer,
        ForeignKey("shelves.id")
    )

    shelf = relationship(
        "Shelf",
        back_populates="products"
    )