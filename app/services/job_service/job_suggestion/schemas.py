from typing import Any, List, Optional
from pydantic import BaseModel
from uuid import UUID


class SuggestionProfileResponse(BaseModel):
    profile_text: str
    generated_at: str


class TopRecommendedJobMatch(BaseModel):
    job_id: Optional[int] = None
    job_name: Optional[str] = None
    score: Optional[float] = None
    reason: Optional[str] = None


class JobSuggestionResponse(BaseModel):
    recommendation: Optional[TopRecommendedJobMatch] = None
    analysis_completed_at: str


class UserDataSummary(BaseModel):
    dreamer_id: UUID
    init_answers_count: int
    good_jobs_count: int
    bad_jobs_count: int
    saved_jobs_count: int
    total_jobs_viewed: int


class SuggestionDebugResponse(BaseModel):
    dreamer_id: UUID
    user_data_summary: UserDataSummary
    profile: SuggestionProfileResponse
    recommendations: List[Any]
