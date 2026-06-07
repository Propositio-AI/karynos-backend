from typing import Any

from app.services.job_service.job_suggestion.recommendation import RuleBasedProfileGenerator


class JobSuggestionAnalyzer:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def analyze_user_profile(self, user_data: dict[str, Any]):
        init_answers = user_data.get("init_answers", [])
        recent_jobs = user_data.get("recent_jobs", [])
        return RuleBasedProfileGenerator.generate_profile(init_answers, recent_jobs)

    def extract_job_traits_from_profile(self, profile: str):
        return {"profile": profile}
