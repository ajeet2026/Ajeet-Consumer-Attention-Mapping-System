from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Shelf(Base):

    __tablename__ = "shelves"

    id = Column(Integer, primary_key=True, index=True)

    shelf_name = Column(String)

    category = Column(String)