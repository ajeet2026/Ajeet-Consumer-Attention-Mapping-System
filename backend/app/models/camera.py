from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    ip_address = Column(String)

    store_id = Column(
        Integer,
        ForeignKey("stores.id")
    )

    store = relationship(
        "Store",
        back_populates="cameras"
    )