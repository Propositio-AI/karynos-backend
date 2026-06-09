from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.gateways import job_gateway
from app.services.job.schema import (
    JobDetailResponse,
    JobSearchResponse,
    JobSearchResult,
    ViewingHistoryItem,
    ViewingHistoryResponse,
)


class JobService:
    def get_job_detail(self, job_id: int):
        response = job_gateway.get_job(job_id)
        if not response["success"] or not response["data"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="job が見つかりません"
            )

        job = response["data"][0]
        payload = {
            "job_id": getattr(job, "job_id", 0),
            "name": getattr(job, "name", "") or "",
            "description": getattr(job, "description", "") or "",
            "imgs": getattr(job, "imgs", []) or [],
            "salary": int(getattr(job, "salary", 0) or 0),
            "level": int(getattr(job, "level", 0) or 0),
            "end_time": getattr(job, "end_time", "") or "",
            "holiday": int(getattr(job, "holiday", 0) or 0),
            "overtime_hours": int(getattr(job, "overtime_hours", 0) or 0),
            "age": int(getattr(job, "age", 0) or 0),
            "tenure_years": int(getattr(job, "tenure_years", 0) or 0),
            "marriage_age": int(getattr(job, "marriage_age", 0) or 0),
            "gender_ratio": float(getattr(job, "gender_ratio", 0.0) or 0.0),
            "romance_rate": float(getattr(job, "romance_rate", 0.0) or 0.0),
            "social_signification": getattr(job, "social_signification", "") or "",
            "personality_traits": getattr(job, "personality_traits", "") or "",
            "growth_opportunities": getattr(job, "growth_opportunities", "") or "",
            "wrong_image": getattr(job, "wrong_image", "") or "",
            "uniform": bool(getattr(job, "uniform", False) or False),
            "work_life_balance": float(getattr(job, "work_life_balance", 0.0) or 0.0),
            "future_outlook": getattr(job, "future_outlook", "") or "",
            "rarity": float(getattr(job, "rarity", 0.0) or 0.0),
            "scandal_history": getattr(job, "scandal_history", "") or "",
            "focus_on_education": bool(
                getattr(job, "focus_on_education", False) or False
            ),
            "focus_on_achievements": bool(
                getattr(job, "focus_on_achievements", False) or False
            ),
            "appeal_points": getattr(job, "appeal_points", "") or "",
            "daily_routine": getattr(job, "daily_routine", "") or "",
            "comments": getattr(job, "comments", "") or "",
            "skills": getattr(job, "skills", []) or [],
            "certifications": getattr(job, "certifications", []) or [],
            "companies": getattr(job, "companies", []) or [],
            "talents": getattr(job, "talents", []) or [],
            "interests": getattr(job, "interests", []) or [],
        }
        return JobDetailResponse.model_validate(payload)

    def get_viewing_history(self, dreamer_id: UUID, limit: int = 50, offset: int = 0):
        response = job_gateway.get_history(dreamer_id)
        if not response["success"]:
            raise HTTPException(status_code=500, detail="閲覧履歴の取得に失敗しました")

        histories = response["data"] or []
        histories = sorted(
            histories,
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True,
        )
        total_count = len(histories)
        paginated_histories = histories[offset : offset + limit]

        items = []
        for history in paginated_histories:
            try:
                job_response = job_gateway.get_job(getattr(history, "job_id", None))
                job = (
                    job_response["data"][0]
                    if job_response["success"] and job_response["data"]
                    else None
                )
                items.append(
                    ViewingHistoryItem(
                        history_id=getattr(history, "history_id"),
                        job_id=getattr(history, "job_id"),
                        job_name=getattr(job, "name", "") if job else "",
                        job_imgs=getattr(job, "imgs", []) if job else [],
                        good=getattr(history, "good", False),
                        bad=getattr(history, "bad", False),
                        save=getattr(history, "save", False),
                        created_at=getattr(
                            history, "created_at", datetime.now()
                        ).isoformat(),
                    )
                )
            except Exception:
                continue
        return ViewingHistoryResponse(
            total_count=total_count, items=items, created_at=datetime.now().isoformat()
        )

    def search_jobs(self, q: str, limit: int = 20, offset: int = 0):
        if not q or not q.strip():
            raise HTTPException(status_code=400, detail="検索クエリが空です")
        if limit < 1 or limit > 100:
            limit = 20
        if offset < 0:
            offset = 0

        from app.algorithm.job_suggestion.recommendation import VectorSearchRecommender

        recommender = VectorSearchRecommender()
        if not recommender.is_ready():
            raise HTTPException(
                status_code=500,
                detail="ベクトルDB（Qdrant）に接続できません。管理者に連絡してください。",
            )

        hits = recommender.search_by_text(q.strip(), top_k=limit + offset)
        if not hits:
            return JobSearchResponse(
                query=q, total_count=0, items=[], created_at=datetime.now().isoformat()
            )

        items = []
        for hit in hits[offset : offset + limit]:
            try:
                job_response = job_gateway.get_job(int(hit["job_id"]))
                if not job_response["success"] or not job_response["data"]:
                    continue
                job = job_response["data"][0]
                items.append(
                    JobSearchResult(
                        job_id=getattr(job, "job_id"),
                        name=getattr(job, "name", "") or "",
                        description=getattr(job, "description", "") or "",
                        imgs=getattr(job, "imgs", []) or [],
                        personality_traits=getattr(job, "personality_traits", "") or "",
                        appeal_points=getattr(job, "appeal_points", "") or "",
                        growth_opportunities=getattr(job, "growth_opportunities", "")
                        or "",
                        similarity_score=hit["score"],
                    )
                )
            except Exception:
                continue
        return JobSearchResponse(
            query=q,
            total_count=len(hits),
            items=items,
            created_at=datetime.now().isoformat(),
        )

    def mark_history(self, history_id: UUID, payload: dict[str, bool]):
        response = job_gateway.update_history(history_id, payload)
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["message"])
        return status.HTTP_200_OK

    def sync_jobs_to_vectordb(self, rebuild: bool = False):
        from app.algorithm.job_suggestion.recommendation import VectorSearchRecommender

        jobs_response = job_gateway.list_jobs()
        if not jobs_response["success"]:
            messages = jobs_response.get("message") or []
            detail = "職業データ取得に失敗しました"
            if messages:
                detail = f"{detail}: {messages[0]}"
            raise HTTPException(status_code=500, detail=detail)

        jobs = jobs_response["data"] or []
        recommender = VectorSearchRecommender()
        if not recommender.is_ready():
            raise HTTPException(
                status_code=500, detail="ベクトルDB（Qdrant）への接続に失敗しました"
            )

        synced = recommender.sync_jobs(jobs, rebuild=rebuild)
        mode = "rebuild" if rebuild else "upsert"
        return {
            "message": f"{mode} sync completed",
            "synced_count": synced,
            "total_jobs": len(jobs),
            "completed_at": datetime.now().isoformat(),
        }


job_service = JobService()
