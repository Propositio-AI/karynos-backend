from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from app.services.dreamer_service.schemas import (
	DreamerGroupResponse,
	DreamerResponse,
	DreamerToGroupRequest,
	DreamerToGroupResponse,
	GetInitQuestionsResponse,
	InitAnswersSubmitResponse,
	NewDreamerGroupRequest,
	NewDreamerGroupResponse,
	NewDreamerRequest,
	NewDreamerResponse,
	SubmitInitAnswersRequest,
	UpdateDreamerGroupRequest,
	UpdateDreamerRequest,
	UserInitialAnswerHistoryResponse,
)
from app.services.dreamer_service.services.dreamer_service import dreamer_service
from app.lib.auth import get_current_user_id

router = APIRouter(prefix="/dreamer")
api_router = APIRouter(prefix="/api/v1")


@api_router.post("/admin/new", response_model=NewDreamerResponse)
async def create_dreamer(request: NewDreamerRequest):
	return dreamer_service.create_dreamer(request)


@api_router.get("/admin/{dreamer_id}", response_model=DreamerResponse)
async def get_dreamer(dreamer_id: str):
	return dreamer_service.get_dreamer(dreamer_id)


@api_router.put("/admin/{dreamer_id}", response_model=DreamerResponse)
async def update_dreamer(dreamer_id: str, request: UpdateDreamerRequest):
	return dreamer_service.update_dreamer(dreamer_id, request)


@api_router.delete("/admin/{dreamer_id}", response_model=DreamerResponse)
async def delete_dreamer(dreamer_id: str):
	return dreamer_service.delete_dreamer(dreamer_id)


@api_router.post("/groups/new", response_model=NewDreamerGroupResponse)
async def create_group(request: NewDreamerGroupRequest):
	return dreamer_service.create_group(request)


@api_router.get("/groups/{group_id}", response_model=DreamerGroupResponse)
async def get_group(group_id: str):
	return dreamer_service.get_group(group_id)


@api_router.put("/groups/{group_id}", response_model=DreamerGroupResponse)
async def update_group(group_id: str, request: UpdateDreamerGroupRequest):
	return dreamer_service.update_group(group_id, request)


@api_router.delete("/groups/{group_id}", response_model=DreamerGroupResponse)
async def delete_group(group_id: str):
	return dreamer_service.delete_group(group_id)


@api_router.put("/groups/{group_id}/add_dreamer", response_model=DreamerToGroupResponse)
async def add_dreamer_to_group(group_id: str, request: DreamerToGroupRequest):
	return dreamer_service.add_dreamer_to_group(group_id, request)


@api_router.delete("/groups/{group_id}/remove_dreamer", response_model=DreamerToGroupResponse)
async def remove_dreamer_from_group(group_id: str, request: DreamerToGroupRequest):
	return dreamer_service.remove_dreamer_from_group(group_id, request)


@api_router.get("/init-questions", response_model=GetInitQuestionsResponse)
async def get_init_questions(version: int = 1):
	try:
		return dreamer_service.get_init_questions(version)
	except HTTPException:
		raise
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc))


@api_router.post("/init-answers", response_model=InitAnswersSubmitResponse)
async def submit_init_answers(
	request: SubmitInitAnswersRequest,
	user_id: UUID = Depends(get_current_user_id),
):
	try:
		return dreamer_service.submit_init_answers(request, user_id)
	except HTTPException:
		raise
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc))


@api_router.get("/init-answers/history", response_model=list[UserInitialAnswerHistoryResponse])
async def get_init_answers_history(
	user_id: UUID = Depends(get_current_user_id),
):
	try:
		return dreamer_service.get_init_answers_history(user_id)
	except HTTPException:
		raise
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc))


router.include_router(api_router)
