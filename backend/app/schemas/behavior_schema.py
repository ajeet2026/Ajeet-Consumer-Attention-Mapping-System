from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BehaviorProfileBase(BaseModel):
    session_id: int
    shopper_id: int
    visit_duration: float
    zones_visited: int
    products_viewed: int
    products_picked: int
    comparisons: int
    total_attention_seconds: float
    preferred_category: Optional[str] = None
    segment: str
    confidence: float
    journey_path: List[str]

class BehaviorProfileCreate(BehaviorProfileBase):
    pass

class BehaviorProfileResponse(BehaviorProfileBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SegmentDistributionResponse(BaseModel):
    segment: str
    count: int
    percentage: float
