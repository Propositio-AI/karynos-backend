from fastapi import APIRouter
from schemas import (
    NewMentorRequest, NewMentorResponse,MentorResponse,
    UpdateMentorRequest, NewMentorGroupRequest,NewMentorGroupResponse,
    MentorGroupResponse,UpdataMentorGroupRequest, MentorToGroupRequest,
    MentorToGroupResponse
)

# /api/v1/mentor

router = APIRouter(prefix="/v1", tags=["mentor"])

# =============
# Mentor Admin
# =============

@router.post("/admin/new",response_model=NewMentorResponse)
async def create_mentor(request: NewMentorRequest):
    """新しいMentorアカウントを作成する"""
    pass


