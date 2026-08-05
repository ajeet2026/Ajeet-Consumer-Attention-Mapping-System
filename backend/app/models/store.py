from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    location = Column(String, nullable=False)

    manager_name = Column(String, nullable=True)

    shelves = relationship(
        "Shelf",
        back_populates="store",
        cascade="all, delete"
    )

    cameras = relationship(
        "Camera",
        back_populates="store",
        cascade="all, delete"
    )