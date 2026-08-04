from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Store(Base):

    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)

    store_name = Column(String)

    location = Column(String)