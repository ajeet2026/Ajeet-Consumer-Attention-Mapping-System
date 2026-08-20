from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.scoring import ProductScore
from app.models.product import Product
from app.models.shelf import Shelf
from app.models.tracking import ZoneEvent
from app.models.interaction import ProductInteraction

class RecommendationEngine:
    """
    Phase 9: Recommendation & Optimization Engine
    Analyzes consumer behavior, attention data, and product scores to generate
    actionable retail intelligence insights.
    """

    @staticmethod
    def generate_all_recommendations(db: Session):
        recommendations = []
        
        # 1. Product Placement Recommendations (Hidden Gems vs Overexposed duds)
        product_recs = RecommendationEngine._analyze_products(db)
        recommendations.extend(product_recs)
        
        # 2. Shelf & Layout Optimization
        layout_recs = RecommendationEngine._analyze_layout(db)
        recommendations.extend(layout_recs)
        
        return {
            "insights": recommendations,
            "summary": {
                "total_recommendations": len(recommendations),
                "high_priority": len([r for r in recommendations if r.get("priority") == "High"])
            }
        }

    @staticmethod
    def _analyze_products(db: Session):
        insights = []
        scores = db.query(ProductScore).join(Product).all()
        
        for score in scores:
            product = score.product
            
            # Scenario A: High Attention, Low Purchase (Needs Promotion)
            if score.attention_score > 70 and score.purchase_score < 30:
                insights.append({
                    "type": "Promotional Suggestion",
                    "priority": "High",
                    "target": product.name,
                    "insight": f"'{product.name}' gets massive attention ({score.attention_score}%) but converts poorly ({score.purchase_score}%).",
                    "action": "Add a promotional discount or check if the price is turning shoppers away."
                })
                
            # Scenario B: Low Attention, High Purchase (Hidden Gem)
            elif score.attention_score < 40 and score.purchase_score > 60:
                shelf_name = product.shelf.name if product.shelf else "unknown shelf"
                insights.append({
                    "type": "Product Placement",
                    "priority": "High",
                    "target": product.name,
                    "insight": f"'{product.name}' is a hidden gem. It has low visibility ({score.attention_score}%) but excellent conversion when found ({score.purchase_score}%).",
                    "action": f"Move it from '{shelf_name}' to a higher-traffic zone like the Entrance or End-cap display."
                })
                
            # Scenario C: High Pickup, Low Purchase (Quality/Packaging Issue)
            elif score.pickup_score > 70 and score.purchase_score < 20:
                insights.append({
                    "type": "Merchandising Alert",
                    "priority": "Medium",
                    "target": product.name,
                    "insight": f"Shoppers pick up '{product.name}' frequently but put it back.",
                    "action": "Check product expiration dates, packaging damage, or clarify confusing labeling."
                })

        return insights

    @staticmethod
    def _analyze_layout(db: Session):
        insights = []
        
        # Calculate traffic (number of unique visits) and average dwell time per zone
        zone_stats = db.query(
            ZoneEvent.zone_id,
            func.count(ZoneEvent.id).label("visits"),
            func.avg(ZoneEvent.duration).label("avg_dwell")
        ).group_by(ZoneEvent.zone_id).all()
        
        if not zone_stats:
            return insights

        # Find max visits to establish a baseline
        max_visits = max([z.visits for z in zone_stats])
        
        for zone in zone_stats:
            if not zone.zone_id or zone.zone_id in ["Checkout", "Entrance"]:
                continue # Skip non-shelf zones for layout analysis
                
            traffic_ratio = zone.visits / max_visits if max_visits > 0 else 0
            
            # Scenario A: High Traffic, Low Dwell Time (Missed Opportunity)
            if traffic_ratio > 0.7 and zone.avg_dwell and zone.avg_dwell < 10.0:
                insights.append({
                    "type": "Layout Optimization",
                    "priority": "High",
                    "target": f"Zone: {zone.zone_id}",
                    "insight": f"'{zone.zone_id}' gets high foot traffic but shoppers rush past it (Avg dwell: {round(zone.avg_dwell, 1)}s).",
                    "action": "Place visual disruptors, digital signage, or highly engaging premium products to slow shoppers down."
                })
                
            # Scenario B: Low Traffic, High Dwell Time (Destination Zone)
            elif traffic_ratio < 0.4 and zone.avg_dwell and zone.avg_dwell > 30.0:
                insights.append({
                    "type": "Store Routing",
                    "priority": "Medium",
                    "target": f"Zone: {zone.zone_id}",
                    "insight": f"'{zone.zone_id}' is a cold zone, but those who visit stay a long time (Avg dwell: {round(zone.avg_dwell, 1)}s).",
                    "action": "Route traffic toward this destination zone by placing essentials or 'magnet' products on the path leading to it."
                })

        return insights
