from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models.product import Product
from app.models.scoring import ProductScore
from app.models.interaction import ProductInteraction
from app.models.attention import AttentionEvent
from app.models.tracking import TrackingSession

class ScoringEngine:
    """
    Phase 8: Product Attractiveness Scoring Engine
    Implements the Weighted Scoring Model from the official specification.
    """
    
    # Weights defined in PDF
    WEIGHTS = {
        "attention": 0.35,      # Attention Duration (35%)
        "interaction": 0.25,    # Product Interaction Frequency (25%)
        "pickup": 0.20,         # Product Pickup Rate (20%)
        "purchase": 0.15,       # Purchase Conversion Rate (15%)
        "repeat": 0.05          # Repeat Engagement Rate (5%)
    }

    @staticmethod
    def calculate_all_scores(db: Session):
        """Calculates and updates attractiveness scores for all products in the store."""
        products = db.query(Product).all()
        
        # Get baseline max values to normalize scores (relative scoring)
        # 1. Max Attention Duration
        max_attention = db.query(func.sum(AttentionEvent.duration)).group_by(AttentionEvent.shelf_id).order_by(func.sum(AttentionEvent.duration).desc()).first()
        max_attention_val = max_attention[0] if max_attention and max_attention[0] else 1.0

        for product in products:
            ScoringEngine._calculate_product_score(db, product.id, product.shelf_id, max_attention_val)

    @staticmethod
    def _calculate_product_score(db: Session, product_id: int, shelf_id: int, max_attention_val: float):
        # 1. Attention Duration (35%)
        # Since attention is tracked by shelf, we use shelf attention as a proxy for product attention visibility
        attention_sum = db.query(func.sum(AttentionEvent.duration)).filter(AttentionEvent.shelf_id == shelf_id).scalar() or 0.0
        attention_score = min(100.0, (attention_sum / max_attention_val) * 100.0)

        # 2. Product Interaction Frequency (25%)
        # Total interactions (views, picks, etc)
        total_interactions = db.query(ProductInteraction).filter(ProductInteraction.product_id == product_id).count()
        # Normalize: Assume 50 interactions per cycle is "100%" highly interactive
        interaction_score = min(100.0, (total_interactions / 50.0) * 100.0)

        # 3. Product Pickup Rate (20%)
        # ratio of "picked_up" to total interactions
        pickups = db.query(ProductInteraction).filter(
            ProductInteraction.product_id == product_id, 
            ProductInteraction.interaction_type == "picked_up"
        ).count()
        pickup_score = 0.0
        if total_interactions > 0:
            pickup_score = (pickups / total_interactions) * 100.0

        # 4. Purchase Conversion Rate (15%)
        # ratio of "purchased" to "picked_up"
        purchases = db.query(ProductInteraction).filter(
            ProductInteraction.product_id == product_id, 
            ProductInteraction.interaction_type == "purchased"
        ).count()
        purchase_score = 0.0
        if pickups > 0:
            purchase_score = min(100.0, (purchases / pickups) * 100.0)

        # 5. Repeat Engagement Rate (5%)
        # Shoppers who interacted with it in multiple distinct sessions
        repeat_engagements = db.query(
            ProductInteraction.session_id, func.count(ProductInteraction.id)
        ).filter(ProductInteraction.product_id == product_id).group_by(ProductInteraction.session_id).having(func.count(ProductInteraction.id) > 1).count()
        
        unique_shoppers = db.query(ProductInteraction.session_id).filter(ProductInteraction.product_id == product_id).distinct().count()
        
        repeat_score = 0.0
        if unique_shoppers > 0:
            repeat_score = (repeat_engagements / unique_shoppers) * 100.0

        # CALCULATE FINAL WEIGHTED SCORE
        final_score = (
            (attention_score * ScoringEngine.WEIGHTS["attention"]) +
            (interaction_score * ScoringEngine.WEIGHTS["interaction"]) +
            (pickup_score * ScoringEngine.WEIGHTS["pickup"]) +
            (purchase_score * ScoringEngine.WEIGHTS["purchase"]) +
            (repeat_score * ScoringEngine.WEIGHTS["repeat"])
        )

        # Save to Database
        score_record = db.query(ProductScore).filter(ProductScore.product_id == product_id).first()
        if not score_record:
            score_record = ProductScore(product_id=product_id)
            db.add(score_record)

        score_record.attention_score = round(attention_score, 2)
        score_record.interaction_score = round(interaction_score, 2)
        score_record.pickup_score = round(pickup_score, 2)
        score_record.purchase_score = round(purchase_score, 2)
        score_record.repeat_score = round(repeat_score, 2)
        score_record.final_attractiveness_score = round(final_score, 2)
        score_record.last_calculated = datetime.utcnow()

        db.commit()
        return score_record
