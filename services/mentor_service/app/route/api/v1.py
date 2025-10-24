from fastapi import APIRouter
from crud import mentors_crud, mentor_groups_crud, mentor_group_members_crud
from schemas import (
    NewMentorRequest, NewMentorResponse,MentorResponse,
    UpdateMentorRequest, NewMentorGroupRequest,NewMentorGroupResponse,
    MentorGroupResponse,UpdateMentorGroupRequest, MentorToGroupRequest,
    MentorToGroupResponse
)

# /api/v1/mentor

router = APIRouter()

# ====================
# Mentor Admin
# ====================

@router.post("/admin/new", response_model=NewMentorResponse)
async def create_mentor(request: NewMentorRequest):
    """新しいMentorアカウントを作成"""
    _, result, _=mentors_crud.create(request)
    return result

@router.get("/admin/{mentor_id}", response_model=MentorResponse)
async def get_mentor(mentor_id: str):
    """Mentor情報を取得"""
    _, result, _=mentors_crud.read(
        [
            ["mentor_id", "==", mentor_id]
        ]
    )
    return result[0] if result else None

@router.put("/admin/{mentor_id}", response_model=MentorResponse)
async def update_mentor(mentor_id: str, request: UpdateMentorRequest):
    """Mentor情報を更新"""
    _, result, _=mentors_crud.update(
        [
            ["mentor_id", "==", mentor_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    return result


@router.delete("/admin/{mentor_id}", response_model=MentorResponse)
async def delete_mentor(mentor_id: str):
    """Mentor情報を削除"""
    _, result, _=mentors_crud.delete(
        [
            ["mentor_id", "==", mentor_id]
        ]
    )
    return result

# ====================
# Mentor Groups
# ====================

@router.post("/groups/new", response_model=NewMentorGroupResponse)
async def create_group(request: NewMentorGroupRequest):
    """新しいMentorグループを作成"""
    _, result, _=mentor_groups_crud.create(request)
    return result

@router.get("/groups/{group_id}", response_model=MentorGroupResponse)
async def get_group(group_id: str):
    """Mentorグループの情報を取得"""
    _, result, _=mentor_groups_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    return result[0] if result else None


@router.put("/groups/{group_id}", response_model=MentorGroupResponse)
async def update_group(group_id: str, request: UpdateMentorGroupRequest):
    """Mentorグループの情報を更新"""
    _, result, _=mentor_groups_crud.update(
        [
            ["group_id", "==", group_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    return result

@router.delete("/groups/{group_id}", response_model=MentorGroupResponse)
async def delete_group(group_id: str):
    """Mentorグループを削除"""
    _, result, _=mentor_groups_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    return result


# ====================
# Mentor Group Members
# ====================

@router.post("/groups/{group_id}/add_mentor", response_model=MentorToGroupResponse)
async def add_mentor_to_group(group_id: str, request: MentorToGroupRequest):
    """Mentorをグループに追加"""
    added_mentors=[]
    for mentor_id in request.mentors:
        data={"group_id": group_id, "mentor_id": mentor_id}
        _, result, _=mentor_group_members_crud.create(data)
        added_mentors.append(result)
    return {"mentors": added_mentors}

@router.post("/groups/{group_id}/remove_mentor", response_model=MentorToGroupResponse)
async def remove_mentor_from_group(group_id: str, request: MentorToGroupRequest):
    """Mentorをグループから削除"""
    _, result, _=mentor_group_members_crud.delete(
        [
            ["group_id", "==", group_id],
            ["mentor_id", "in", request.mentors]
        ]
    )
    return {"mentors": result}
