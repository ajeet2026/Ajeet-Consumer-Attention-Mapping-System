class SegmentationService:
    """
    Phase 7: Consumer segmentation
    Implement the five segments specified by the project:
    Explorer, Quick Buyer, Comparison Shopper, Impulse Buyer, Brand Loyal Customer.
    """
    
    @staticmethod
    def classify_segment(features: dict, preference: dict, journey: dict, historical_sessions: int = 0, historical_repeat_brand: bool = False):
        zones = features.get("zones_visited", 0)
        products = features.get("products_viewed", 0)
        duration = features.get("visit_duration", 0.0)
        comparisons = features.get("comparisons", 0)
        picks = features.get("products_picked", 0)
        
        # 1. Brand Loyal Customer -> repeated preference for the same brand across sessions
        if historical_sessions > 1 and historical_repeat_brand:
            return "Brand Loyal Customer", 0.90
            
        # 2. Explorer -> many zones + many products + longer journey
        if zones >= 3 and products >= 5 and duration > 60:
            return "Explorer", 0.85
            
        # 3. Comparison Shopper -> many product views + repeated comparisons
        if comparisons > 0 and products >= 3:
            return "Comparison Shopper", 0.80
            
        # 4. Quick Buyer -> short visit + few interactions
        if duration < 40 and zones <= 1:
            return "Quick Buyer", 0.85
            
        # 5. Impulse Buyer -> short decision + interaction/pickup with little comparison
        if picks > 0 and comparisons == 0 and duration < 45:
            return "Impulse Buyer", 0.75
            
        # Default fallback
        if duration < 40:
            return "Quick Buyer", 0.70
            
        return "Browser", 0.50
