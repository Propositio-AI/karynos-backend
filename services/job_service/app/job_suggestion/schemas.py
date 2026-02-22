"""
Job Suggestion Schemas

責務:
- リクエスト/レスポンスモデルの定義
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from schema import JobDetailResponse


class SuggestionProfileResponse(BaseModel):
    """生成されたユーザープロファイル"""
    profile_text: str = Field(..., description="AI生成されたプロファイル（400文字程度）")
    generated_at: str = Field(..., description="生成日時（ISO 8601形式）")
    
    model_config = ConfigDict(from_attributes=True)


class RecommendedJobInfo(BaseModel):
    """推奨職業の基本情報"""
    job_id: int = Field(..., description="職業ID")
    job_name: str = Field(..., description="職業名")
    similarity_score: float = Field(..., description="適合度スコア（0-100）")
    job_analysis: str = Field(..., description="職業の分析データ")
    
    model_config = ConfigDict(from_attributes=True)


class JobRecommendationWithHistory(RecommendedJobInfo):
    """推奨職業と過去の評価情報"""
    rank: int = Field(..., description="推奨順位")
    previously_viewed: bool = Field(..., description="過去に閲覧したか")
    previous_good: bool = Field(..., description="過去にGood評価したか")
    previous_bad: bool = Field(..., description="過去にBad評価したか")
    previous_save: bool = Field(..., description="過去に保存したか")
    history_id: Optional[str] = Field(None, description="過去の履歴ID（存在する場合）")
    
    model_config = ConfigDict(from_attributes=True)


class TopRecommendedJobMatch(BaseModel):
    """マッチング画面用：最もおすすめの職業データ"""
    job_id: int = Field(..., description="職業ID")
    imgs: List[str] = Field(..., description="職業の画像")
    name: str = Field(..., description="職業名")
    salary: int = Field(..., description="平均年収")
    similarity_score: float = Field(..., description="適合度（0-100）")
    age: int = Field(..., description="平均年齢")
    description: str = Field(..., description="業務内容")
    history_id: str = Field(..., description="閲覧履歴ID")
    
    model_config = ConfigDict(from_attributes=True)


class JobSuggestionResponse(BaseModel):
    """Job Suggestionのレスポンス"""
    recommendation: Optional[TopRecommendedJobMatch] = Field(None, description="最もおすすめの職業")
    analysis_completed_at: str = Field(..., description="分析完了日時（ISO 8601形式）")
    
    model_config = ConfigDict(from_attributes=True)


class UserDataSummary(BaseModel):
    """分析に使用されたユーザーデータの概要"""
    dreamer_id: UUID = Field(..., description="ユーザーID")
    init_answers_count: int = Field(..., description="初期質問への回答数")
    good_jobs_count: int = Field(..., description="Good評価した職業数")
    bad_jobs_count: int = Field(..., description="Bad評価した職業数")
    saved_jobs_count: int = Field(..., description="保存した職業数")
    total_jobs_viewed: int = Field(..., description="閲覧した職業総数")
    
    model_config = ConfigDict(from_attributes=True)


class SuggestionDebugResponse(BaseModel):
    """デバッグ用：分析プロセスの詳細"""
    dreamer_id: UUID = Field(..., description="ユーザーID")
    user_data_summary: UserDataSummary = Field(..., description="ユーザーデータ概要")
    profile: SuggestionProfileResponse = Field(..., description="生成されたプロファイル")
    recommendations: List[JobRecommendationWithHistory] = Field(..., description="推奨職業")
    
    model_config = ConfigDict(from_attributes=True)
