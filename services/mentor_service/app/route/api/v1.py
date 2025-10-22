from fastapi import APIRouter
from schemas import (
    NewMentorRequest, NewMentorResponse,MentorResponse,
    UpdateMentorRequest, NewMentorGroupRequest,NewMentorGroupResponse,
    MentorGroupResponse,UpdateMentorGroupRequest, MentorToGroupRequest,
    MentorToGroupResponse
)

# /api/v1/mentor

router = APIRouter()

# =============
# Mentor Admin
# =============

@router.post("/admin/new", response_model=NewMentorResponse)
async def create_mentor(request: NewMentorRequest):
    """新しいMentorアカウントを作成"""
    pass

@router.get("/admin/{mentor_id}", response_model=MentorResponse)
async def get_mentor(mentor_id: str):
    """Mentor情報を取得"""
    pass

@router.put("/admin/{mentor_id}", response_model=MentorResponse)
async def update_mentor(mentor_id: str, request: UpdateMentorRequest):
    """Mentor情報を更新"""
    pass

@router.delete("/admin/{mentor_id}", response_model=MentorResponse)
async def delete_mentor(mentor_id: str):
    """Mentor情報を削除"""
    pass

# =============
#Mentor Group
# =============

@router.post("/groups/new", response_model=NewMentorGroupResponse)
async def create_group(request: NewMentorGroupRequest):
    """新しいMentorグループを作成"""
    pass

@router.get("/groups/{group_id}", response_model=MentorGroupResponse)
async def get_group(group_id: str):
    """Mentorグループの情報を取得"""
    pass

@router.put("/groups/{group_id}", response_model=MentorGroupResponse)
async def update_group(group_id: str, request: UpdateMentorGroupRequest):
    """Mentorグループの情報を更新"""
    pass

@router.delete("/groups/{group_id}", response_model=MentorGroupResponse)
async def delete_group(group_id: str):
    """Mentorグループを削除"""
    pass

# =============
# Group Members
# =============

@router.post("/groups/{group_id}/add_mentor", response_model=MentorToGroupResponse)
async def add_mentor_to_group(group_id: str, request: MentorToGroupRequest):
    """Mentorをグループに追加"""
    pass

@router.post("/groups/{group_id}/remove_mentor", response_model=MentorToGroupResponse)
async def remove_mentor_from_group(group_id: str, request: MentorToGroupRequest):
    """Mentorをグループから削除"""
    pass