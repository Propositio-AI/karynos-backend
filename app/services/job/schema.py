from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobData(BaseModel):
    name: str = Field(..., description="jobs.name")
    imgs: list[str] = Field(..., description="職業ごとの画像データリンク")
    salary: int = Field(..., description="jobs_feedback.salary")
    level: int = Field(..., description="jobs_feedback.level")


class RecommendResponse(BaseModel):
    job_id: int = Field(..., description="jobs.job_id")
    history_id: UUID = Field(..., description="histories.history_id")
    job_data: JobData = Field(..., description="職業データ情報")

    model_config = ConfigDict(from_attributes=True)


class Skill(BaseModel):
    skill_id: int
    name: str
    is_required: bool


class Certification(BaseModel):
    certification_id: int
    name: str
    is_required: bool


class Company(BaseModel):
    company_id: int
    name: str


class Talent(BaseModel):
    talent_id: int
    name: str
    is_required: bool


class Interest(BaseModel):
    interest_id: int
    name: str
    is_required: bool


class JobDetailResponse(BaseModel):
    job_id: int
    name: str
    description: str
    imgs: list[str]
    salary: int
    level: int
    end_time: str
    holiday: int
    overtime_hours: int
    age: int
    tenure_years: int
    marriage_age: int
    gender_ratio: float
    romance_rate: float
    social_signification: str
    personality_traits: str
    growth_opportunities: str
    wrong_image: str
    uniform: bool
    work_life_balance: float
    future_outlook: str
    rarity: float
    scandal_history: str
    focus_on_education: bool
    focus_on_achievements: bool
    appeal_points: str
    daily_routine: str
    comments: str
    skills: list[Skill]
    certifications: list[Certification]
    companies: list[Company]
    talents: list[Talent]
    interests: list[Interest]

    model_config = ConfigDict(from_attributes=True)


class ViewingHistoryItem(BaseModel):
    history_id: UUID
    job_id: int
    job_name: str
    job_imgs: list[str]
    good: bool
    bad: bool
    save: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ViewingHistoryResponse(BaseModel):
    total_count: int
    items: list[ViewingHistoryItem]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class JobSearchResult(BaseModel):
    job_id: int
    name: str
    description: str
    imgs: list[str]
    personality_traits: str
    appeal_points: str
    growth_opportunities: str
    similarity_score: float

    model_config = ConfigDict(from_attributes=True)


class JobSearchResponse(BaseModel):
    query: str
    total_count: int
    items: list[JobSearchResult]
    created_at: str

    model_config = ConfigDict(from_attributes=True)
