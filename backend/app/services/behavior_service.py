from sqlalchemy.orm import Session
from app.models.tracking import TrackingSession
from app.models.behavior import BehaviorProfile
from app.services.behavior_features import BehaviorFeaturesService
from app.services.preference_service import PreferenceService
from app.services.journey_service import JourneyService
from app.services.segmentation_service import SegmentationService

class BehaviorService:
    """
    Phase 1, 8, 9: Orchestrator
    Combines all results and creates the behavior profile.
    """
    
    @staticmethod
    def analyze_completed_session(db: Session, session_id: int):
        # 1. Fetch Session
        session = db.query(TrackingSession).filter(TrackingSession.id == session_id).first()
        if not session:
            return None
            
        shopper_id = session.tracking_id
        
        # 2. Features Layer
        features = BehaviorFeaturesService.calculate_features(db, session)
        
        # 3 & 4. Preference Layer
        preferences = PreferenceService.analyze_preferences(db, session_id)
        
        # 5 & 6. Journey Layer
        journey = JourneyService.analyze_journey(db, session_id)
        
        # 8. Historical Behavior Layer
        # Check if they have past sessions with same preferred category
        past_profiles = db.query(BehaviorProfile).filter(BehaviorProfile.shopper_id == shopper_id).all()
        historical_sessions = len(past_profiles)
        historical_repeat_brand = False
        if past_profiles and preferences["preferred_category"]:
            for pp in past_profiles:
                if pp.preferred_category == preferences["preferred_category"]:
                    historical_repeat_brand = True
                    break
        
        # 7. Segmentation Layer
        segment, confidence = SegmentationService.classify_segment(
            features, preferences, journey, historical_sessions, historical_repeat_brand
        )
        
        # 9. Create Profile
        profile = BehaviorProfile(
            session_id=session_id,
            shopper_id=shopper_id,
            visit_duration=features["visit_duration"],
            zones_visited=features["zones_visited"],
            products_viewed=features["products_viewed"],
            products_picked=features["products_picked"],
            comparisons=features["comparisons"],
            total_attention_seconds=features["total_attention_seconds"],
            preferred_category=preferences["preferred_category"],
            segment=segment,
            confidence=confidence,
            journey_path=journey["journey_path"]
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
