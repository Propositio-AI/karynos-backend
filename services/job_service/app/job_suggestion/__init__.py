"""
Job Suggestion Package

職業推奨システムの中核コンポーネント

責務分割:
- data_fetcher.py: dreamer_serviceとjob_serviceからのデータ取得
- analyzer.py: OpenAIを使用した適性分析
- recommendation.py: ベクトル検索と推奨処理
- schemas.py: スキーマ定義
"""

from .data_fetcher import DreamerServiceClient, JobHistoryDataFetcher, DataAggregator
from .analyzer import JobSuggestionAnalyzer
from .recommendation import VectorSearchRecommender, RecommendationProcessor, RuleBasedProfileGenerator
from .schemas import (
    SuggestionProfileResponse,
    RecommendedJobInfo,
    JobRecommendationWithHistory,
    TopRecommendedJobMatch,
    JobSuggestionResponse,
    UserDataSummary,
    SuggestionDebugResponse
)

__all__ = [
    # Data Fetchers
    "DreamerServiceClient",
    "JobHistoryDataFetcher",
    "DataAggregator",
    # Analyzer
    "JobSuggestionAnalyzer",
    # Recommendation
    "VectorSearchRecommender",
    "RecommendationProcessor",
    "RuleBasedProfileGenerator",
    # Schemas
    "SuggestionProfileResponse",
    "RecommendedJobInfo",
    "JobRecommendationWithHistory",
    "TopRecommendedJobMatch",
    "JobSuggestionResponse",
    "UserDataSummary",
    "SuggestionDebugResponse",
]
