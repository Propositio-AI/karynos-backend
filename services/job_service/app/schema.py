from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import List

class JobData(BaseModel):
    name: str = Field(..., description="jobs.name")
    imgs: List[str] = Field(..., description="職業ごとの画像データリンク")
    salary: int = Field(..., description="jobs_feedback.salary")
    level: int = Field(..., description="jobs_feedback.level")

class RecommendResponse(BaseModel):
    job_id: int = Field(..., description="jobs.job_id")
    history_id: UUID = Field(..., description="histories.history_id")
    job_data: JobData = Field(..., description="職業データ情報")

    model_config = ConfigDict(from_attributes=True)

class Skill(BaseModel):
    skill_id: int = Field(..., description="skills.skill_id")
    name: str = Field(..., description="skills.name")
    is_required: bool = Field(..., description="skills.is_required")


class Certification(BaseModel):
    certification_id: int = Field(..., description="certifications.certification_id")
    name: str = Field(..., description="certifications.name")
    is_required: bool = Field(..., description="certifications.is_required")


class Company(BaseModel):
    company_id: int = Field(..., description="companies.company_id")
    name: str = Field(..., description="companies.name")


class Talent(BaseModel):
    talent_id: int = Field(..., description="talents.talent_id")
    name: str = Field(..., description="talents.name")
    is_required: bool = Field(..., description="talents.is_required")


class Interest(BaseModel):
    interest_id: int = Field(..., description="interests.interest_id")
    name: str = Field(..., description="interests.name")
    is_required: bool = Field(..., description="interests.is_required")


class JobDetailResponse(BaseModel):
    job_id: int = Field(..., description="jobs.job_id")
    name: str = Field(..., description="jobs.name")
    description: str = Field(..., description="jobs.description")
    imgs: List[str] = Field(..., description="職業の画像データリンク")
    salary: int = Field(..., description="jobs_feedback.salary")
    level: int = Field(..., description="jobs_feedback.level")
    end_time: str = Field(..., description="勤務終了時刻（例: '18:00'）")
    holiday: int = Field(..., description="休日数")
    overtime_hours: int = Field(..., description="残業時間")
    age: int = Field(..., description="平均年齢")
    tenure_years: int = Field(..., description="平均勤続年数")
    marriage_age: int = Field(..., description="平均結婚年齢")
    gender_ratio: float = Field(..., description="男女比")
    romance_rate: float = Field(..., description="社内恋愛率")
    social_signification: str = Field(..., description="社会的意義")
    personality_traits: str = Field(..., description="求められる性格特性")
    growth_opportunities: str = Field(..., description="成長機会")
    wrong_image: str = Field(..., description="誤解されやすいイメージ")
    uniform: bool = Field(..., description="制服の有無")
    work_life_balance: float = Field(..., description="ワークライフバランス評価")
    future_outlook: str = Field(..., description="将来性")
    rarity: float = Field(..., description="希少度")
    scandal_history: str = Field(..., description="過去のスキャンダル履歴")
    focus_on_education: bool = Field(..., description="教育重視か")
    focus_on_achievements: bool = Field(..., description="実績重視か")
    appeal_points: str = Field(..., description="アピールポイント")
    daily_routine: str = Field(..., description="1日の流れ")
    comments: str = Field(..., description="コメント")
    skills: List[Skill] = Field(..., description="必要スキルリスト")
    certifications: List[Certification] = Field(..., description="必要資格リスト")
    companies: List[Company] = Field(..., description="関連企業リスト")
    talents: List[Talent] = Field(..., description="求められる才能リスト")
    interests: List[Interest] = Field(..., description="関連興味リスト")

    model_config = ConfigDict(from_attributes=True)


class ViewingHistoryItem(BaseModel):
    """閲覧履歴の単一アイテム"""
    history_id: UUID = Field(..., description="histories.history_id")
    job_id: int = Field(..., description="jobs.job_id")
    job_name: str = Field(..., description="jobs.name")
    job_imgs: List[str] = Field(..., description="職業の画像リスト")
    good: bool = Field(..., description="いいねフラグ")
    bad: bool = Field(..., description="バッドフラグ")
    save: bool = Field(..., description="保存フラグ")
    created_at: str = Field(..., description="閲覧日時（ISO 8601形式）")

    model_config = ConfigDict(from_attributes=True)


class ViewingHistoryResponse(BaseModel):
    """閲覧履歴一覧レスポンス"""
    total_count: int = Field(..., description="総閲覧数")
    items: List[ViewingHistoryItem] = Field(..., description="閲覧履歴アイテムリスト")
    created_at: str = Field(..., description="レスポンス生成時刻（ISO 8601形式）")

    model_config = ConfigDict(from_attributes=True)


class JobSearchResult(BaseModel):
    """職業検索結果の単一アイテム"""
    job_id: int = Field(..., description="jobs.job_id")
    name: str = Field(..., description="jobs.name")
    description: str = Field(..., description="jobs.description")
    imgs: List[str] = Field(..., description="職業の画像リスト")
    personality_traits: str = Field(..., description="求められる性格特性")
    appeal_points: str = Field(..., description="アピールポイント")
    growth_opportunities: str = Field(..., description="成長機会")
    similarity_score: float = Field(..., description="検索クエリとの類似度スコア（0-100）")

    model_config = ConfigDict(from_attributes=True)


class JobSearchResponse(BaseModel):
    """職業検索レスポンス"""
    query: str = Field(..., description="検索クエリ")
    total_count: int = Field(..., description="マッチした職業数")
    items: List[JobSearchResult] = Field(..., description="職業検索結果リスト")
    created_at: str = Field(..., description="レスポンス生成時刻（ISO 8601形式）")

    model_config = ConfigDict(from_attributes=True)