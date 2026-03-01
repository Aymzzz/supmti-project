"""
Eligibility API router – checks student eligibility for programs.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from app.services.eligibility_service import eligibility_service

router = APIRouter()


class EligibilityRequest(BaseModel):
    diploma: str = Field(..., description="Student's diploma type")
    note: Optional[float] = Field(None, description="Student's grade (out of 20)")
    specialty: Optional[str] = Field(None, description="Area of interest/specialty")


class ProgramResult(BaseModel):
    program_id: str
    program_name: str
    program_name_en: str = ""
    program_name_darija: str = ""
    description: str = ""
    status: str
    reasons: List[str] = []
    relevance: int = 0


class EligibilityResponse(BaseModel):
    eligible: List[ProgramResult]
    conditional: List[ProgramResult]
    not_eligible: List[ProgramResult]
    summary: str


@router.post("/check", response_model=EligibilityResponse)
async def check_eligibility(request: EligibilityRequest):
    """Check student eligibility for all programs."""
    result = eligibility_service.check_eligibility(
        diploma=request.diploma,
        note=request.note,
        specialty=request.specialty,
    )
    return result


@router.get("/programs")
async def list_programs():
    """List all available programs with their requirements."""
    programs = eligibility_service.get_all_programs()
    return {"programs": programs}
