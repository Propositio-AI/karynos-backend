from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.lib.auth import get_current_user_id
from app.services.job_service.job_suggestion.schemas import JobSuggestionResponse, SuggestionDebugResponse
from app.services.job_service.schema import JobDetailResponse, JobSearchResponse, ViewingHistoryResponse
from app.services.job_service.services.job_service import job_service

router = APIRouter(prefix="/job")
api_router = APIRouter(prefix="/api/v1")


@api_router.get("/detail/{job_id}", response_model=JobDetailResponse)
async def get_job_detail(job_id: int):
	return job_service.get_job_detail(job_id)


@api_router.get("/history", response_model=ViewingHistoryResponse)
async def get_viewing_history(
	dreamer_id: UUID = Depends(get_current_user_id),
	limit: int = 50,
	offset: int = 0,
):
	return job_service.get_viewing_history(dreamer_id, limit, offset)


@api_router.get("/search", response_model=JobSearchResponse)
async def search_jobs(q: str, limit: int = 20, offset: int = 0):
	return job_service.search_jobs(q, limit, offset)


@api_router.put("/good/{history_id}", status_code=status.HTTP_200_OK)
async def mark_good(history_id: UUID):
	return job_service.mark_history(history_id, {"good": True})


@api_router.put("/bad/{history_id}", status_code=status.HTTP_200_OK)
async def mark_bad(history_id: UUID):
	return job_service.mark_history(history_id, {"bad": True})


@api_router.put("/save/{history_id}", status_code=status.HTTP_200_OK)
async def mark_save(history_id: UUID):
	job_service.mark_history(history_id, {"save": True})
	return {"message": "保存登録が完了しました"}


@api_router.get("/recommend", response_model=JobSuggestionResponse)
async def recommend_jobs(dreamer_id: UUID = Depends(get_current_user_id)):
	return job_service.recommend_jobs(dreamer_id)


@api_router.get("/recommend/debug", response_model=SuggestionDebugResponse)
async def recommend_jobs_debug(dreamer_id: UUID = Depends(get_current_user_id)):
	return job_service.recommend_jobs_debug(dreamer_id)


@api_router.post("/admin/sync-chromadb", status_code=status.HTTP_200_OK)
async def sync_jobs_to_chromadb():
	return job_service.sync_jobs_to_chromadb()


router.include_router(api_router)
