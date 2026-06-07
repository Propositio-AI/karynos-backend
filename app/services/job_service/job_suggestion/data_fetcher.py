from datetime import datetime
from uuid import UUID

from app.gateways import dreamer_gateway, job_gateway


class DreamerServiceClient:
    @classmethod
    def get_init_answers_history(cls, dreamer_id: UUID):
        response = dreamer_gateway.list_answer_history(str(dreamer_id))
        if not response.get("success"):
            return None

        result = []
        for answer in response.get("data") or []:
            question_response = dreamer_gateway.get_answer_question(str(answer.question_id))
            option_response = dreamer_gateway.get_answer_option(str(answer.option_id))

            question_text = ""
            if question_response.get("success") and question_response.get("data"):
                question_text = getattr(question_response["data"][0], "question_text", "") or ""

            option_text = ""
            if option_response.get("success") and option_response.get("data"):
                option_text = getattr(option_response["data"][0], "option_text", "") or ""

            result.append(
                {
                    "answer_id": str(getattr(answer, "answer_id", "")),
                    "question_id": str(getattr(answer, "question_id", "")),
                    "question_text": question_text,
                    "option_id": str(getattr(answer, "option_id", "")),
                    "option_text": option_text,
                    "question_version": int(getattr(answer, "question_version", 1) or 1),
                    "answered_at": (
                        getattr(answer, "answered_at", None).isoformat()
                        if getattr(answer, "answered_at", None)
                        else ""
                    ),
                }
            )
        return result


class JobHistoryDataFetcher:
    @staticmethod
    def get_user_job_history(dreamer_id: UUID):
        response = job_gateway.get_history(dreamer_id)
        if not response.get("success"):
            return None

        histories = sorted(
            response.get("data") or [],
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True,
        )

        good_jobs = []
        bad_jobs = []
        saved_jobs = []

        for history in histories:
            job_id = getattr(history, "job_id", None)
            job_name = ""
            if job_id is not None:
                job_response = job_gateway.get_job(int(job_id))
                if job_response.get("success") and job_response.get("data"):
                    job_name = getattr(job_response["data"][0], "name", "") or ""

            item = {
                "history_id": str(getattr(history, "history_id", "")),
                "job_id": int(job_id or 0),
                "job_name": job_name,
                "good": bool(getattr(history, "good", False)),
                "bad": bool(getattr(history, "bad", False)),
                "save": bool(getattr(history, "save", False)),
                "created_at": (
                    getattr(history, "created_at", None).isoformat()
                    if getattr(history, "created_at", None)
                    else ""
                ),
            }
            if item["good"]:
                good_jobs.append(item)
            if item["bad"]:
                bad_jobs.append(item)
            if item["save"]:
                saved_jobs.append(item)

        return {
            "total_jobs_viewed": len(histories),
            "good_jobs": good_jobs,
            "bad_jobs": bad_jobs,
            "saved_jobs": saved_jobs,
        }

    @staticmethod
    def get_recent_viewed_jobs(dreamer_id: UUID, limit: int = 10):
        response = job_gateway.get_history(dreamer_id)
        if not response.get("success"):
            return []

        histories = sorted(
            response.get("data") or [],
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True,
        )[:limit]

        jobs = []
        for history in histories:
            job_id = getattr(history, "job_id", None)
            if job_id is None:
                continue
            job_response = job_gateway.get_job(int(job_id))
            if not job_response.get("success") or not job_response.get("data"):
                continue
            job = job_response["data"][0]
            jobs.append(
                {
                    "job_id": int(getattr(job, "job_id", 0) or 0),
                    "name": getattr(job, "name", "") or "",
                    "description": getattr(job, "description", "") or "",
                    "salary": int(getattr(job, "salary", 0) or 0),
                    "age": int(getattr(job, "age", 0) or 0),
                    "personality_traits": getattr(job, "personality_traits", "") or "",
                    "appeal_points": getattr(job, "appeal_points", "") or "",
                    "growth_opportunities": getattr(job, "growth_opportunities", "") or "",
                    "good": bool(getattr(history, "good", False)),
                    "bad": bool(getattr(history, "bad", False)),
                    "save": bool(getattr(history, "save", False)),
                }
            )
        return jobs


class DataAggregator:
    @staticmethod
    def aggregate_user_data(dreamer_id: UUID):
        init_answers = DreamerServiceClient.get_init_answers_history(dreamer_id)
        job_history = JobHistoryDataFetcher.get_user_job_history(dreamer_id)
        recent_jobs = JobHistoryDataFetcher.get_recent_viewed_jobs(dreamer_id)

        if init_answers is None or job_history is None:
            return None

        return {
            "dreamer_id": str(dreamer_id),
            "init_answers": init_answers,
            "job_history": job_history,
            "recent_jobs": recent_jobs,
        }
