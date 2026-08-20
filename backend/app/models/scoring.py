from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class ProductScore(Base):
    """
    Stores the calculated attractiveness score for each product based on the weighted model.
    """
    __tablename__ = "product_scores"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), unique=True, index=True)
    
    # Raw normalized metric scores (0.0 to 100.0)
    attention_score = Column(Float, default=0.0)      # 35%
    interaction_score = Column(Float, default=0.0)    # 25%
    pickup_score = Column(Float, default=0.0)         # 20%
    purchase_score = Column(Float, default=0.0)       # 15%
    repeat_score = Column(Float, default=0.0)         # 5%
    
    # Final weighted score (0 to 100)
    final_attractiveness_score = Column(Float, default=0.0)
    
    last_calculated = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product")
