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
from .schemas import (
    SuggestionProfileResponse,
    TopRecommendedJobMatch,
    JobSuggestionResponse,
    UserDataSummary,
    SuggestionDebugResponse,
)

__all__ = [
    # Data Fetchers
    "DreamerServiceClient",
    "JobHistoryDataFetcher",
    "DataAggregator",
    "JobSuggestionAnalyzer",
    "VectorSearchRecommender",
    "RecommendationProcessor",
    "RuleBasedProfileGenerator",
    # Schemas
    "SuggestionProfileResponse",
    "TopRecommendedJobMatch",
    "JobSuggestionResponse",
    "UserDataSummary",
    "SuggestionDebugResponse",
]


def __getattr__(name: str):
    if name == "JobSuggestionAnalyzer":
        from .analyzer import JobSuggestionAnalyzer

        return JobSuggestionAnalyzer
    if name in {"VectorSearchRecommender", "RecommendationProcessor", "RuleBasedProfileGenerator"}:
        from .recommendation import RecommendationProcessor, RuleBasedProfileGenerator, VectorSearchRecommender

        return {
            "VectorSearchRecommender": VectorSearchRecommender,
            "RecommendationProcessor": RecommendationProcessor,
            "RuleBasedProfileGenerator": RuleBasedProfileGenerator,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
