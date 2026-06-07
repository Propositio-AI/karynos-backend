from dataclasses import dataclass
from typing import Any

from app.gateways.db.base_prisma_gateway import BasePrismaGateway
from app.gateways.db.prisma_client import run_prisma
from app.gateways.result import GatewayResult
from app.gen.prisma import types as prisma_types
from app.gen.prisma.models import History, Job


@dataclass
class JobProjection:
    job_id: int | None
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
    skills: list[dict[str, Any]]
    certifications: list[dict[str, Any]]
    companies: list[dict[str, Any]]
    talents: list[dict[str, Any]]
    interests: list[dict[str, Any]]


class JobGateway(BasePrismaGateway):
    JOB = "job"
    HISTORY = "history"

    def _normalize_job(self, job: Job) -> JobProjection:
        feedbacks = list(getattr(job, "job_feedbacks", []) or [])
        feedback = feedbacks[0] if feedbacks else None

        def _val(name: str, default: Any):
            if feedback is None:
                return default
            value = getattr(feedback, name, default)
            return default if value is None else value

        skills = []
        for item in list(getattr(feedback, "feedback_skill", []) or []):
            skill = getattr(item, "skill", None)
            if skill is None:
                continue
            skills.append(
                {
                    "skill_id": getattr(skill, "skill_id", None),
                    "name": getattr(skill, "name", None),
                    "is_required": getattr(item, "is_required", False),
                }
            )

        certifications = []
        for item in list(getattr(feedback, "feedback_certification", []) or []):
            cert = getattr(item, "certification", None)
            if cert is None:
                continue
            certifications.append(
                {
                    "certification_id": getattr(cert, "certification_id", None),
                    "name": getattr(cert, "name", None),
                    "is_required": getattr(item, "is_required", False),
                }
            )

        companies = []
        for item in list(getattr(feedback, "feedback_company", []) or []):
            company = getattr(item, "company", None)
            if company is None:
                continue
            companies.append(
                {
                    "company_id": getattr(company, "company_id", None),
                    "name": getattr(company, "name", None),
                }
            )

        talents = []
        for item in list(getattr(feedback, "feedback_talent", []) or []):
            talent = getattr(item, "talent", None)
            if talent is None:
                continue
            talents.append(
                {
                    "talent_id": getattr(talent, "talent_id", None),
                    "name": getattr(talent, "name", None),
                    "is_required": getattr(item, "is_required", False),
                }
            )

        interests = []
        for item in list(getattr(feedback, "feedback_interest", []) or []):
            interest = getattr(item, "interest", None)
            if interest is None:
                continue
            interests.append(
                {
                    "interest_id": getattr(interest, "interest_id", None),
                    "name": getattr(interest, "name", None),
                    "is_required": getattr(item, "is_required", False),
                }
            )

        return JobProjection(
            job_id=getattr(job, "job_id", None),
            name=getattr(job, "name", "") or "",
            description=getattr(job, "description", "") or "",
            imgs=[getattr(image, "img_url", "") for image in list(getattr(job, "job_images", []) or [])],
            salary=_val("salary", 0),
            level=_val("level", 0),
            end_time=(getattr(feedback, "end_time", None).isoformat() if feedback and getattr(feedback, "end_time", None) else ""),
            holiday=_val("holiday", 0),
            overtime_hours=_val("overtime_hours", 0),
            age=_val("age", 0),
            tenure_years=_val("tenure_years", 0),
            marriage_age=_val("marriage_age", 0),
            gender_ratio=_val("gender_ratio", 0.0),
            romance_rate=_val("romance_rate", 0.0),
            social_signification=_val("social_signification", ""),
            personality_traits=_val("personality_traits", ""),
            growth_opportunities=_val("growth_opportunities", ""),
            wrong_image=_val("wrong_image", ""),
            uniform=_val("uniform", False),
            work_life_balance=_val("work_life_balance", 0.0),
            future_outlook=_val("future_outlook", ""),
            rarity=_val("rarity", 0.0),
            scandal_history=_val("scandal_history", ""),
            focus_on_education=_val("focus_on_education", False),
            focus_on_achievements=_val("focus_on_achievements", False),
            appeal_points=_val("appeal_points", ""),
            daily_routine=_val("daily_routine", ""),
            comments=_val("comments", ""),
            skills=skills,
            certifications=certifications,
            companies=companies,
            talents=talents,
            interests=interests,
        )

    def _job_include(self) -> dict[str, Any]:
        return {
            "job_images": True,
            "job_feedbacks": {
                "include": {
                    "feedback_skill": {"include": {"skill": True}},
                    "feedback_certification": {"include": {"certification": True}},
                    "feedback_company": {"include": {"company": True}},
                    "feedback_talent": {"include": {"talent": True}},
                    "feedback_interest": {"include": {"interest": True}},
                }
            },
        }

    def get_job(self, job_id: int) -> GatewayResult[list[JobProjection]]:
        try:
            rows = run_prisma(
                self.prisma.job.find_many(
                    where={"job_id": int(job_id)},
                    include=self._job_include(),
                )
            )
            normalized = [self._normalize_job(row) for row in rows]
            return {"success": True, "message": ["Success"], "data": normalized}
        except Exception as exc:
            return {"success": False, "message": [str(exc)], "data": None}

    def list_jobs(self) -> GatewayResult[list[JobProjection]]:
        try:
            rows = run_prisma(self.prisma.job.find_many(include=self._job_include()))
            normalized = [self._normalize_job(row) for row in rows]
            return {"success": True, "message": ["Success"], "data": normalized}
        except Exception as exc:
            return {"success": False, "message": [str(exc)], "data": None}

    def get_history(self, dreamer_id: Any) -> GatewayResult[list[History]]:
        return self.find_many(self.HISTORY, {"dreamer_id": str(dreamer_id)})

    def update_history(
        self,
        history_id: Any,
        payload: prisma_types.HistoryUpdateInput | dict[str, Any],
    ) -> GatewayResult[list[History]]:
        return self.update_many_and_fetch(self.HISTORY, {"history_id": str(history_id)}, payload)


job_gateway = JobGateway()
