from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database.database import get_db
from app.models.behavior import BehaviorProfile
from app.schemas.behavior_schema import BehaviorProfileResponse, SegmentDistributionResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/behavior", tags=["Behavior Intelligence"])

@router.get("/segments", response_model=List[SegmentDistributionResponse])
def get_segment_distribution(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get the distribution of consumer segments across all historical tracking sessions.
    """
    total_count = db.query(BehaviorProfile).count()
    if total_count == 0:
        return []
        
    segments = db.query(
        BehaviorProfile.segment, 
        func.count(BehaviorProfile.id).label('count')
    ).group_by(BehaviorProfile.segment).all()
    
    result = []
    for seg, count in segments:
        result.append(
            SegmentDistributionResponse(
                segment=seg,
                count=count,
                percentage=round((count / total_count) * 100, 2)
            )
        )
    return result

@router.get("/preferences/leaderboard")
def get_product_preferences(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get a leaderboard of preferred product categories.
    """
    categories = db.query(
        BehaviorProfile.preferred_category, 
        func.count(BehaviorProfile.id).label('count')
    ).filter(BehaviorProfile.preferred_category != None).group_by(BehaviorProfile.preferred_category).order_by(func.count(BehaviorProfile.id).desc()).all()
    
    return [{"category": c, "count": count} for c, count in categories]

@router.get("/journeys/analytics")
def get_journey_analytics(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Extract aggregated journey analytics: top routes, transitions, and metrics.
    """
    profiles = db.query(BehaviorProfile).all()
    
    total_shoppers = len(profiles)
    if total_shoppers == 0:
        return {
            "total_shoppers": 0,
            "avg_journey_time": 0,
            "avg_path_length": 0,
            "top_routes": [],
            "zone_transitions": [],
            "zone_heat": {}
        }
        
    total_time = sum(p.visit_duration for p in profiles)
    
    routes_count = {}
    transitions = {}
    zone_heat = {}
    total_path_length = 0
    
    for p in profiles:
        path = p.journey_path
        if not path:
            continue
            
        total_path_length += len(path)
        
        # Count routes
        route_str = " → ".join(path)
        routes_count[route_str] = routes_count.get(route_str, 0) + 1
        
        # Count zone heat and transitions
        for i, zone in enumerate(path):
            zone_heat[zone] = zone_heat.get(zone, 0) + 1
            if i < len(path) - 1:
                next_zone = path[i+1]
                trans_key = f"{zone} → {next_zone}"
                transitions[trans_key] = transitions.get(trans_key, 0) + 1
                
    # Sort and format top routes
    top_routes = [
        {"route": k, "count": v, "percentage": round((v / total_shoppers) * 100, 1)}
        for k, v in sorted(routes_count.items(), key=lambda item: item[1], reverse=True)[:5]
    ]
    
    # Sort transitions
    top_transitions = [
        {"transition": k, "count": v}
        for k, v in sorted(transitions.items(), key=lambda item: item[1], reverse=True)[:10]
    ]
    
    return {
        "total_shoppers": total_shoppers,
        "avg_journey_time": round(total_time / total_shoppers),
        "avg_path_length": round(total_path_length / total_shoppers, 1) if total_shoppers > 0 else 0,
        "top_routes": top_routes,
        "zone_transitions": top_transitions,
        "zone_heat": zone_heat
    }

@router.get("/session/{session_id}", response_model=BehaviorProfileResponse)
def get_session_behavior(session_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get the behavior profile of a specific shopper session.
    """
    profile = db.query(BehaviorProfile).filter(BehaviorProfile.session_id == session_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Behavior profile not found for this session")
        
    return profile
