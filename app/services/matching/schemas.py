from typing import Any
from uuid import UUID

from pydantic import BaseModel


class TopRecommendedJobMatch(BaseModel):
    job_id: int
    imgs: list[str]
    name: str
    salary: int
    similarity_score: float
    age: int
    description: str
    history_id: str


class MatchingResponse(BaseModel):
    recommendation: TopRecommendedJobMatch
    analysis_completed_at: str


class MatchingProfileSummary(BaseModel):
    profile_text: str
    generated_at: str


class MatchingUserDataSummary(BaseModel):
    dreamer_id: UUID
    init_answers_count: int
    good_jobs_count: int
    bad_jobs_count: int
    saved_jobs_count: int
    total_jobs_viewed: int


class MatchingDebugResponse(BaseModel):
    dreamer_id: UUID
    user_data_summary: MatchingUserDataSummary
    profile: MatchingProfileSummary
    recommendations: list[Any]
