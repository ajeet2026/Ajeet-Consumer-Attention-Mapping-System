from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Camera(Base):

    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)

    camera_name = Column(String)

    zone = Column(String)

    status = Column(String)