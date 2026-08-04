from sqlalchemy import Column, Integer, String, Float

from app.database.database import Base


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    product_name = Column(String)

    brand = Column(String)

    price = Column(Float)