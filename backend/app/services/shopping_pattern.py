class ShoppingPatternService:
    """
    Phase 3: Shopping pattern analysis
    Use features to characterize the shopper's shopping pattern.
    """
    
    @staticmethod
    def analyze(features: dict):
        zones = features.get("zones_visited", 0)
        products = features.get("products_viewed", 0)
        duration = features.get("visit_duration", 0.0)
        
        pattern = "Average Shopper"
        
        if zones > 3 and products > 5 and duration > 60:
            pattern = "High Exploration"
        elif zones <= 2 and duration < 30 and features.get("products_picked", 0) == 0:
            pattern = "Fast Shopping"
        elif features.get("comparisons", 0) > 0 and duration > 45:
            pattern = "Comparative Shopping"
        elif features.get("products_picked", 0) > 0 and duration < 40:
            pattern = "Targeted Buying"
            
        return {
            "pattern_label": pattern,
            "exploration_score": min(1.0, (zones * 0.2) + (duration / 300.0))
        }
