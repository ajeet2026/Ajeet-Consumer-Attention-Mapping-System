from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database.database import get_db
from app.models.product import Product
from app.models.scoring import ProductScore
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/analytics/products", tags=["Product Analytics"])

@router.get("/scores")
def get_product_scores(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get the attractiveness scores of all products, sorted by final score.
    """
    scores = db.query(ProductScore).join(Product).order_by(desc(ProductScore.final_attractiveness_score)).all()
    
    result = []
    for score in scores:
        result.append({
            "product_id": score.product.id,
            "product_name": score.product.name,
            "brand": score.product.brand,
            "shelf": score.product.shelf.name if score.product.shelf else "Unknown",
            "scores": {
                "attention_score": score.attention_score,
                "interaction_score": score.interaction_score,
                "pickup_score": score.pickup_score,
                "purchase_score": score.purchase_score,
                "repeat_score": score.repeat_score,
                "final_score": score.final_attractiveness_score
            },
            "last_calculated": score.last_calculated
        })
        
    return result

@router.post("/scores/calculate")
def trigger_score_calculation(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Manually trigger the scoring engine to recalculate all product scores.
    """
    from app.services.scoring_engine import ScoringEngine
    ScoringEngine.calculate_all_scores(db)
    return {"message": "Product attractiveness scores calculated successfully"}

@router.get("/recommendations")
def get_ai_recommendations(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Generate AI-driven text recommendations based on behavioral analytics and product scores.
    """
    from app.services.recommendation_engine import RecommendationEngine
    return RecommendationEngine.generate_all_recommendations(db)
