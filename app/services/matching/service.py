from datetime import datetime
from uuid import UUID

from fastapi import HTTPException

from app.algorithm.job_suggestion.recommendation import (
    RecommendationProcessor,
    RuleBasedProfileGenerator,
    VectorSearchRecommender,
)
from app.gateways import dreamer_gateway, job_gateway
from app.services.matching.schemas import (
    MatchingDebugResponse,
    MatchingProfileSummary,
    MatchingResponse,
    MatchingUserDataSummary,
    TopRecommendedJobMatch,
)


class MatchingService:
    def _fetch_init_answers(self, dreamer_id: UUID) -> list[dict]:
        response = dreamer_gateway.list_answer_history(str(dreamer_id))
        if not response.get("success"):
            return []

        result = []
        for answer in response.get("data") or []:
            q = dreamer_gateway.get_answer_question(str(answer.question_id))
            o = dreamer_gateway.get_answer_option(str(answer.option_id))
            result.append(
                {
                    "question_text": (
                        q["data"][0].question_text if q["success"] and q["data"] else ""
                    ),
                    "option_text": (
                        o["data"][0].option_text if o["success"] and o["data"] else ""
                    ),
                }
            )
        return result

    def _fetch_job_history(self, dreamer_id: UUID) -> tuple[list[dict], dict]:
        response = job_gateway.get_history(dreamer_id)
        if not response.get("success"):
            return [], {
                "total_jobs_viewed": 0,
                "good_jobs": [],
                "bad_jobs": [],
                "saved_jobs": [],
            }

        histories = sorted(
            response.get("data") or [],
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True,
        )

        recent_jobs: list[dict] = []
        good_jobs: list[dict] = []
        bad_jobs: list[dict] = []
        saved_jobs: list[dict] = []

        for history in histories:
            job_id = getattr(history, "job_id", None)
            if job_id is None:
                continue
            job_response = job_gateway.get_job(int(job_id))
            job = (
                job_response["data"][0]
                if job_response.get("success") and job_response.get("data")
                else None
            )

            item = {
                "job_id": int(job_id),
                "name": getattr(job, "name", "") or "" if job else "",
                "good": bool(getattr(history, "good", False)),
                "bad": bool(getattr(history, "bad", False)),
                "save": bool(getattr(history, "save", False)),
            }
            recent_jobs.append(item)
            if item["good"]:
                good_jobs.append(item)
            if item["bad"]:
                bad_jobs.append(item)
            if item["save"]:
                saved_jobs.append(item)

        summary = {
            "total_jobs_viewed": len(histories),
            "good_jobs": good_jobs,
            "bad_jobs": bad_jobs,
            "saved_jobs": saved_jobs,
        }
        return recent_jobs, summary

    def _build_recommender(self) -> VectorSearchRecommender:
        recommender = VectorSearchRecommender()
        if not recommender.is_ready():
            raise HTTPException(
                status_code=503,
                detail="ベクトルDB（Qdrant）に接続できません。先に /api/v1/job/admin/sync-vectordb を実行してください。",
            )
        return recommender

    def recommend(self, dreamer_id: UUID) -> MatchingResponse:
        init_answers = self._fetch_init_answers(dreamer_id)
        recent_jobs, _ = self._fetch_job_history(dreamer_id)
        profile_text = RuleBasedProfileGenerator.generate_profile(
            init_answers, recent_jobs
        )

        recommender = self._build_recommender()
        results = RecommendationProcessor(recommender).generate_recommendations(
            profile=profile_text, recent_jobs=recent_jobs, top_k=10
        )

        if not results:
            raise HTTPException(
                status_code=404, detail="推薦できる職業が見つかりませんでした"
            )

        top = results[0]
        job_id = int(top.get("job_id", 0) or 0)

        job_response = job_gateway.get_job(job_id)
        if not job_response["success"] or not job_response["data"]:
            raise HTTPException(
                status_code=404, detail="推薦職業の詳細データが取得できませんでした"
            )
        job = job_response["data"][0]

        history_response = job_gateway.create_history(dreamer_id, job_id)
        if not history_response["success"] or not history_response["data"]:
            raise HTTPException(status_code=500, detail="閲覧履歴の作成に失敗しました")
        history_id = str(getattr(history_response["data"], "history_id", ""))

        recommendation = TopRecommendedJobMatch(
            job_id=job_id,
            imgs=getattr(job, "imgs", []) or [],
            name=getattr(job, "name", "") or "",
            salary=int(getattr(job, "salary", 0) or 0),
            similarity_score=float(top.get("score", 0.0) or 0.0),
            age=int(getattr(job, "age", 0) or 0),
            description=getattr(job, "description", "") or "",
            history_id=history_id,
        )

        return MatchingResponse(
            recommendation=recommendation,
            analysis_completed_at=datetime.now().isoformat(),
        )

    def recommend_debug(self, dreamer_id: UUID) -> MatchingDebugResponse:
        init_answers = self._fetch_init_answers(dreamer_id)
        recent_jobs, history_summary = self._fetch_job_history(dreamer_id)
        profile_text = RuleBasedProfileGenerator.generate_profile(
            init_answers, recent_jobs
        )

        recommender = self._build_recommender()
        results = RecommendationProcessor(recommender).generate_recommendations(
            profile=profile_text, recent_jobs=recent_jobs, top_k=10
        )

        return MatchingDebugResponse(
            dreamer_id=dreamer_id,
            user_data_summary=MatchingUserDataSummary(
                dreamer_id=dreamer_id,
                init_answers_count=len(init_answers),
                good_jobs_count=len(history_summary["good_jobs"]),
                bad_jobs_count=len(history_summary["bad_jobs"]),
                saved_jobs_count=len(history_summary["saved_jobs"]),
                total_jobs_viewed=int(history_summary["total_jobs_viewed"]),
            ),
            profile=MatchingProfileSummary(
                profile_text=profile_text,
                generated_at=datetime.now().isoformat(),
            ),
            recommendations=results,
        )


matching_service = MatchingService()
