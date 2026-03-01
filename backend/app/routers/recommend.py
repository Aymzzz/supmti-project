"""
Recommendation API router – suggests programs based on interests.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from app.services.recommendation_service import recommendation_service

router = APIRouter()


class RecommendationRequest(BaseModel):
    interests: List[str] = Field(
        ...,
        description="List of student interests",
        examples=[["informatique", "ai", "web"]],
    )
    diploma: Optional[str] = Field(None, description="Student's diploma")
    note: Optional[float] = Field(None, description="Student's grade")


class RecommendationItem(BaseModel):
    program_id: str
    compatibility_score: int
    raw_score: int
    matched_interests: List[str]


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    top_pick: Optional[RecommendationItem] = None
    message: str


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get program recommendations based on student interests."""
    result = recommendation_service.recommend(
        interests=request.interests,
        diploma=request.diploma,
        note=request.note,
    )
    return result
